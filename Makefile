up:
	docker compose up -d --build

migrate:
	docker compose exec backend alembic upgrade head

new-migration:
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

test:
	docker compose exec backend pytest

