# SQL AGOA Project

## 📊 Database Setup with SQLite

This project includes a Jupyter notebook (`agoa.ipynb`) that contains all SQL commands for:
- Database creation
- Table structure setup
- Data insertion
- Sample queries

To use the database:
1. Open the `agoa.ipynb` file in Jupyter Notebook
2. Execute the cells to create and populate the database

# ✈️ AGOA Project

> A Django-based flight management system that handles airlines, airports, flights, and turnarounds.

## 📋 Prerequisites

- Python 3.12+
- Poetry (Python package manager)

## 🚀 Installation

1. Create a virtual environment:
    ```bash
    python -m venv venv
    # On Unix/macOS
    source venv/bin/activate
    # On Windows
    venv\Scripts\activate
    ```

2. Install Poetry:
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. Install dependencies:
    ```bash
    poetry install
    ```

## 🗄️ Database Setup

1. Activate the Poetry shell:
    ```bash
    poetry shell
    ```

2. Run the following commands to migrate and create a superuser:
    ```bash
    poetry run python manage.py migrate
    poetry run python manage.py makemigrations
    poetry run python manage.py createsuperuser
    ```

## 💻 Running the Development Server

1. Start the server:
    ```bash
    poetry run python manage.py runserver
    ```

2. Access the application:
    - 🔧 Admin interface: [http://localhost:8000/admin](http://localhost:8000/admin)
    - 📚 API documentation: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
    - 🔌 API endpoints: [http://localhost:8000/api/](http://localhost:8000/api/)

## 🔐 API Authentication

The API uses JWT authentication. To access protected endpoints:

1. Get a token from `/api/login/`
2. Include the token in requests using the Authorization header:
    ```http
    Authorization: Bearer <your_token>
    ```

## 📁 Project Structure

- `authentication/`: User authentication and authorization
- `agoa/`: Main application logic for flights and turnarounds
- `tests/`: Test suite
