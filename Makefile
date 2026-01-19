up:
	@echo "[INFO] Starting backend service..."
	docker-compose up -d --no-deps backend

down:
	@echo "[INFO] Stopping backend service..."
	docker-compose down



back:
	@echo "[INFO] Rolling back to previous docker image..."
	@TAG=$(word 2, $(MAKECMDGOALS)); \
	if [ -z "$$TAG" ]; then \
		echo "---------------------------------------------"; \
		echo "AVAILABLE IMAGES:"; \
		docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedSince}}"| grep sha-; \
		echo "---------------------------------------------"; \
		echo "ERROR: Please specify the image tag to roll back to."; \
		echo "Usage: make back <TAG>"; \
		exit 1; \
	fi; \
	echo "[INFO] Rolling back to docker image: $$TAG"; \
	if grep -q "IMAGE_TAG=" .env; then \
		sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=$$TAG/" .env; \
	else \
		echo "IMAGE_TAG=$$TAG" >> .env; \
	fi; \
	docker-compose up -d --no-deps backend
%:
	@:



rollback-migration:
	echo "[INFO] Rolling back last database migration..."
	docker-compose exec -T backend sh -c "alembic downgrade -1"

migrate:
	echo "[INFO] Applying database migrations..."
	docker-compose exec -T backend sh -c "alembic upgrade head"

new-migration:
	echo "[INFO] Creating new database migration..."
	@if [ -z "$(m)" ]; then echo "Error: Please specify migration message using m=\"...\""; exit 1; fi
	docker-compose exec -T backend alembic revision --autogenerate -m "$(m)"

test:
	@echo "[INFO] Running backend tests..."
	docker-compose exec -T  backend pytest






disk-usage:
	@echo "[INFO] Checking disk usage..."
	df -h
	@echo "[INFO] Checking Docker disk usage..."
	docker system df -v
	@echo "[INFO] Listing Docker volumes..."
	docker volume ls
	@echo "[INFO] Listing Docker images..."
	docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"

stats:
	docker stats --no-stream

logs:
	docker-compose logs -f backend