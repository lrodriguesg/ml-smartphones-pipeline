.PHONY: help up down restart logs clean

help:
	@echo "Comandos disponiveis:"
	@echo "  make up      - Sobe toda a infraestrutura em background (Docker Compose)"
	@echo "  make down    - Derruba a infraestrutura e remove os containers"
	@echo "  make restart - Reinicia toda a infraestrutura"
	@echo "  make logs    - Acompanha os logs de todos os containers em tempo real"
	@echo "  make clean   - Derruba a infraestrutura e apaga os volumes (ZERA O BANCO)"

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose down
	docker-compose up -d

logs:
	docker-compose logs -f

clean:
	docker-compose down -v