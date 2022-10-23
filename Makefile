start:
	docker-compose up

start-debug:
	docker-compose -f docker-compose.yml up -d
	docker-compose exec app pip show ipython || pip install ipython --quiet
	docker-compose exec app pip show pudb || pip install pudb --quiet
	docker-compose exec -it app gunicorn -w 1 --worker-class sync --timeout 1000000 -b 0.0.0.0:5050 app:app --reload
	docker-compose -f docker-compose.yml down

test:
	docker-compose exec -it app pip install -r requirements/test.txt
	docker-compose exec -it app python -m flake8 app/**/**/** tests/**/**/**
	docker-compose exec -it app python -m pytest -vv --cov=./app

rebuild:
	docker-compose up --build --force-recreate

rebuild-app:
	docker-compose build app

migrate:
	docker-compose exec app python run_migrations.py

make-migration:
	docker-compose exec app flask db migrate


shell:
	docker-compose exec -it app /bin/bash

py-shell:
	docker-compose exec -it app python run_shell.py
