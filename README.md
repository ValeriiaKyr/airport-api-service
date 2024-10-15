# Airport api

**Airport api** is a project developed using DRF and Docker

# How to run the project

Installing using GitHub:

- Clone the repository:
    https://github.com/ValeriiaKyr/airport-api-service/tree/develop

  - Move into the project directory:
  cd airport_api_service

- Create and activate a virtual environment:

    python -m venv venv
    source venv/bin/activate

- Install the required dependencies:

    pip install -r requirements.txt

- Enter your database connection details and secret key: 
```bash
    set DB_HOST=<your db hostname>

    set DB_NAME=<your db name>

    set DB_USER=<your db username>

    set DB_PASSWORD=<your db user password>
    
    set SECRET_KEY=<your secret key>
```
- Apply the database migrations:

    python manage.py migrate

- Start the development server:

    python manage.py runserver

# Run with docker

Docker should be installed

```bash
docker-compose build
docker-compose up
```
# Getting access

- Create user via /api/v1/user/register/
- Get access token via /api/v1/user/token/

# Features

- JWT authenticated
- Admin panel /admin/
- Documentation is located at /api/v1/swagger/
- Managing orders and tickets
- Creating flight with crew
- Creating routs, airplane, airport, airplane type...
- Filtering flights 
