include .env
export $(shell sed 's/=.*//' .env)

.PHONY: db-clean db-wipe dump-database database-dev dump-database populate-database db-fresh log-database run-server migrate create-user setup setup-log-database setup-run run clean


db-clean :
	venv/bin/python manage.py flush --noinput


db-wipe :
	docker compose -f docker-compose.yml down
	rm -rf volumes/
	docker container prune -f

db-dev-wipe : 
	docker compose -f docker-compose-dev.yml down
	rm -rf volumes/
	docker container prune -f

dump-database :
	venv/bin/python manage.py dumpdata --exclude=auth --exclude=contenttypes --format=json --verbosity=1 --output=geolocations/fixtures/geolocations.json

populate-database :
	venv/bin/python manage.py loaddata geolocations.json

database : docker-compose.yml
	docker compose -f docker-compose.yml up --detach
	sleep 15

database-dev : docker-compose.yml
	docker compose -f docker-compose-dev.yml up --detach
	sleep 15

db-fresh : db-wipe database

log-database :
	docker logs -f postgres_container

venv : requirements.txt
	python3.9 -m venv venv
	venv/bin/python -m pip install wheel
	venv/bin/python -m pip install -r requirements.txt

run-server :
	venv/bin/python manage.py runserver

migrate :
	venv/bin/python manage.py migrate

create-user :
	venv/bin/python manage.py createsuperuser --noinput

setup : venv database migrate create-user populate-database

setup-dev : venv database-dev migrate create-user populate-database

setup-log-database : setup log-database

setup-run : setup run-server

run : database run-server

test:
	venv/bin/python manage.py test

migrations :
	venv/bin/python manage.py makemigrations geolocations

shell :
	venv/bin/python manage.py shell

clean :
	rm -rf venv/