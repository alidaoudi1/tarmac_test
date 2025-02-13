poetry install
poetry shell 
poetry run python .\manage.py migrate
poetry run python .\manage.py makemigrations
poetry run python .\manage.py createsuperuser





