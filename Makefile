.PHONY: up migrate test restore down evidence

up:
	docker compose up -d postgres
	docker compose run --rm migrate
	docker compose up -d api

migrate:
	docker compose run --rm migrate

test:
	docker compose run --rm test

restore:
	docker compose run --rm restore-test

evidence:
	python scripts/write_evidence_manifest.py

down:
	docker compose down
