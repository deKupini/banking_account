# Banking account API
## Installation
Download and install Docker and Docker Compose on your machine according to 
[Docker's official documentation](https://docs.docker.com/engine/install/).
## Configuration
Prepare `.env` file in the main catalog of Django application (where `manage.py` file is stored). The file should 
contain variables like in the example below:  
```
DB_HOST=localhost
DB_NAME=postgres
DB_PASSWORD=postgres
DB_PORT=5432
DB_USER=postgres
```  
The `DB_HOST` should stay as `localhost`.  
  
Using favourite terminal execute the following command in the main catalog: `docker-compose build`.
## Running up API
To run the application execute the following command: `docker-compose up -d`.
All migrations should be executed automatically.  
Before usage, create super user to logging into the app. Follow next steps:  
1. Execute `docker ps` to get ID of your container with Django app (the one with image called banking_account-web).
2. Execute `docker exec -it [CONTAINER_ID] bash`. Now you've got terminal in the container.
3. Execute `python manage.py createsuperuser` and create a user according to your preferences.
4. Log out from the container with `CTRL + D`.
## Usage
The application is available at `localhost:8000` in your browser. At `localhost:8000/swagger/` you will find all 
endpoints of the API.
