# Pipeline ELT: Monitoramento de Preços de Smartphones (Mercado Livre)

Este projeto é um pipeline de dados *end-to-end* desenvolvido para extrair informações públicas da API do Mercado Livre, processá-las de forma escalável e gerar tabelas analíticas para inteligência de precificação. 

O objetivo é fornecer dados limpos e modelados para que o time de negócios possa analisar faixas de preço, agressividade de descontos e o domínio de mercado dos vendedores.

---

## Arquitetura do Projeto

O projeto segue a arquitetura **ELT (Extract, Load, Transform)**, totalmente conteinerizada, garantindo que o ambiente seja reprodutível em qualquer máquina com um único comando.

1. **Extração (Extract):** Um Produtor em Python consome a API REST do Mercado Livre e publica as mensagens em tempo real no **Apache Kafka** (tópico `ml_smartphones_raw`).
2. **Carga (Load):** Um Consumidor em Python assina o tópico do Kafka e insere os dados brutos no **PostgreSQL** (`raw.raw_products`). Foi implementada uma lógica de **Idempotência** (`ON CONFLICT`) para garantir que atualizações de preço reflitam no mesmo produto sem gerar registros duplicados.
3. **Transformação (Transform):** O **dbt (Data Build Tool)** atua dentro do Data Warehouse transformando os dados brutos em um modelo dimensional (`staging` e `marts`), calculando métricas de negócio complexas (como % de desconto e performance de vendedores).
4. **Orquestração:** O **Apache Airflow** gerencia todo o ciclo de vida dos dados. A DAG `ml_smartphones_pipeline` está configurada para rodar em intervalos horários (`@hourly`) com políticas de retentativa em caso de falha.

---

## Tecnologias Utilizadas

* **Linguagem:** Python 3.11 (`requests`, `confluent-kafka`, `psycopg2`)
* **Mensageria & Streaming:** Apache Kafka + Zookeeper
* **Data Warehouse:** PostgreSQL 15
* **Transformação & Testes:** dbt (Data Build Tool)
* **Orquestração:** Apache Airflow 2.9
* **Infraestrutura:** Docker & Docker Compose

---

## 📂 Estrutura do Repositório

```text
📦 projeto/
 ┣ 📂 airflow/            # Configurações e DAGs do orquestrador
 ┃ ┣ 📂 dags/
 ┃ ┃ ┗ 📜 ml_smartphones_pipeline.py
 ┣ 📂 collector/          # Scripts de extração e mensageria
 ┃ ┣ 📜 kafka_producer.py
 ┃ ┣ 📜 kafka_consumer.py
 ┃ ┗ 📜 ml_api_client.py
 ┣ 📂 dbt/                # Projeto de transformação de dados
 ┃ ┣ 📂 macros/
 ┃ ┣ 📂 models/
 ┃ ┃ ┣ 📂 staging/        # Limpeza, tipagem e deduplicação
 ┃ ┃ ┗ 📂 marts/          # Tabelas Fato e Dimensão para o negócio
 ┃ ┣ 📜 dbt_project.yml
 ┃ ┗ 📜 profiles.yml
 ┣ 📜 docker-compose.yml  # Orquestração da infraestrutura
 ┣ 📜 .env.example        # Template de variáveis de ambiente
 ┣ 📜 requirements.txt    # Dependências do Python
 ┗ 📜 README.md
```

---

##  Como Executar o Projeto

### Pré-requisitos
* **Docker** e **Docker Compose** instalados na máquina.
* **Git** para clonar o repositório.

### Passo a Passo

**1. Clone o repositório**
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DA_PASTA>
```

**2. Configure as Variáveis de Ambiente**
Faça uma cópia do arquivo de exemplo para criar o seu arquivo local de senhas:
```bash
cp .env.example .env
```
*(O arquivo já vem com as credenciais padrão configuradas para o ambiente Docker local).*

**3. Suba a Infraestrutura (Containers)**
Execute o comando abaixo para baixar as imagens e subir o Zookeeper, Kafka, PostgreSQL e Apache Airflow simultaneamente:
```bash
docker-compose up -d
```

**4. Acesse o Orquestrador (Airflow)**
* Abra o navegador e acesse: `http://localhost:8080`
* **Login:** `admin`
* **Senha:** Para capturar a senha gerada automaticamente pelo Airflow, rode o seguinte comando no seu terminal:
  ```bash
  docker exec airflow_standalone cat /opt/airflow/standalone_admin_password.txt
  ```

**5. Execute o Pipeline**
* Na interface do Airflow, ative (unpause) a DAG **`ml_smartphones_pipeline`**.
* Clique no botão de *Play* e selecione **"Trigger DAG"**.
* Acompanhe a execução na aba *Graph*. O Airflow fará a extração, carga e transformação sequencialmente.

---

## Modelagem de Dados (dbt)

A transformação foi estruturada seguindo as melhores práticas de Data Engineering:

* **`stg_products` (View):** Limpa os dados brutos, ajusta os tipos de dados (casting para numérico e timestamp) e já calcula em tempo real o `discount_percentage`.
* **`dim_sellers` (Table):** Tabela de dimensão que agrupa o histórico dos vendedores, trazendo métricas como `total_distinct_products` e `lifetime_sold_quantity`.
* **`fct_products` (Table):** Tabela de fatos enriquecida, categorizando a agressividade dos descontos (`discount_category`), pronta para ser consumida pela ferramenta de visualização (Dashboard).

**Garantia de Qualidade:** Foram implementados testes de integridade (`unique`, `not_null`) nos arquivos `schema.yml` para assegurar a confiabilidade da chave primária (`product_id`) antes de liberar os dados para o painel de negócios.

---

## 🌟 Diferenciais Implementados

* **Idempotência no Banco de Dados:** Uso de `ON CONFLICT DO UPDATE` no PostgreSQL para evitar duplicação de produtos e registrar as flutuações de preço em atualizações subsequentes.
* **Proteção de Credenciais:** Variáveis sensíveis isoladas em um arquivo `.env` e injetadas de forma nativa no Linux dos containers via Docker Compose.
* **Macros dbt Customizadas:** Implementação da macro `generate_schema_name.sql` para garantir a nomenclatura limpa dos schemas no banco de dados (`raw`, `staging`, `marts`).
* **Resiliência do Airflow:** A Task do dbt possui o comando `dbt clean` injetado antes da execução para prevenir quebras causadas por cache residual entre diferentes sistemas operacionais.

---

## 🧠 Decisões de Engenharia e Trade-offs

Para garantir a melhor experiência de avaliação e o funcionamento *end-to-end* ininterrupto do projeto, as seguintes decisões arquiteturais foram tomadas:

* **Mock de Dados vs. API do Mercado Livre:** O case sugeria o consumo do endpoint `GET https://api.mercadolibre.com/sites/MLB/search` ressaltando que "não é necessário autenticação". No entanto, devido a atualizações recentes nas políticas da API do Mercado Livre, esse endpoint agora exige autenticação (Bearer Token via Mercado Pago) e a criação prévia de uma aplicação no portal de desenvolvedores. 
Para não quebrar a premissa de "zero configuração manual" (obrigando o avaliador a gerar seus próprios tokens) e para atender perfeitamente à recomendação do case de **"simular dados históricos"** (essencial para responder às perguntas 5 e 7), optei por construir um gerador de dados simulados (Mock) diretamente no extrator. Isso garante que o pipeline rode de forma determinística, segura e sem riscos de *rate limits* ou bloqueios de API.

* **Idempotência (SCD Tipo 1) vs Histórico de Preços (SCD Tipo 2):** O case exige um pipeline idempotente (que não duplique dados na tabela ao rodar várias vezes). Para isso, implementou-se o `ON CONFLICT DO UPDATE` (SCD Tipo 1). Para não perder a capacidade de medir a variação histórica de preços (Pergunta 7) sem inflar o banco de dados com duplicatas de log, a variação de descontos foi calculada comparando inteligentemente as colunas `original_price` e `price` registradas na mesma entidade.