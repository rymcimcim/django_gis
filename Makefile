include .env
export $(shell sed 's/=.*//' .env)

.PHONY: db-down db-clean db-wipe dump-primary-db primary dump-replica populate-primary populate-replica populate db-fresh log-primary run-server migrate create-user setup setup-log-primary setup-run run clean

db-down :
	docker compose down

db-clean : db-down
	rm -rf volumes/
	rm -f db.sqlite3

db-wipe : db-clean
	docker container prune -f

dump-primary :
	venv/bin/python manage.py dumpdata --exclude=auth --exclude=contenttypes --format=json --database=primary --verbosity=1 --output=geolocation/fixtures/geolocation.json

dump-replica :
	venv/bin/python manage.py dumpdata --exclude=auth --exclude=contenttypes --format=json --database=replica --verbosity=1 --output=geolocation/fixtures/geolocation.json

populate-primary :
	venv/bin/python manage.py loaddata geolocation.json --database=primary 

populate-replica :
	venv/bin/python manage.py loaddata geolocation.json --database=replica

populate : populate-primary populate-replica

primary-db : docker-compose.yml
	docker compose up --detach
	sleep 10

db-fresh : db-wipe primary-db

log-primary :
	docker logs -f postgres_container

venv : requirements.txt
	python3.9 -m venv venv
	venv/bin/python -m pip install wheel
	venv/bin/python -m pip install -r requirements.txt

run-server :
	venv/bin/python manage.py runserver

migrate :
	venv/bin/python manage.py migrate --database primary
	venv/bin/python manage.py migrate --database replica

create-user :
	venv/bin/python manage.py createsuperuser --noinput --database primary
	venv/bin/python manage.py createsuperuser --noinput --database replica

setup : venv primary-db migrate create-user populate

setup-log-primary : setup log-primary

setup-run : setup run-server

run : primary-db run-server

migrations :
	venv/bin/python manage.py makemigrations geolocation

shell :
	venv/bin/python manage.py shell

clean :
	rm -rf venv/