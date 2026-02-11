[![Demo Project CI](https://github.com/ItsMilann/demo-project/actions/workflows/ci.yml/badge.svg)](https://github.com/ItsMilann/demo-project/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/ItsMilann/demo-project/graph/badge.svg?token=N90XXYP5T1)](https://codecov.io/github/ItsMilann/demo-project)
# Project Documentation

This documentation guides you through the setup and usage of the Role based CRUD project.

## Features

**Authentication & Roles**
- Roles (Static): Super Admin, Country Admin, Country Member
- JWT token-based authentication
- Role-based permissions and access control

**User Management**
- Super Admin can create Country Admin
- Country Admin can create Country Members for their assigned country only
- Country-based user filtering

**Project CRUD**
- Project belongs to the country and accessible to users of that country only.
- Create Update Delete (soft/hard) for projects
- Role-based access to projects

**Auditlogs**
- Automatically tracks all changes (create, update)
- Auditlogs are readonly.

**Security**
- Password hashing using Django's built-in validators
- JWT token authentication
- Uses .env


## Tech Stack

- **Django 4.2.11** - Web framework
- **Django REST Framework 3.14.0** - REST API framework
- **PostgreSQL** - Database (Changeable to any SQL database by changing .env file)
- **Simple JWT** - JWT authentication
- **Python Decouple** - Environment variable management
- **CORS Headers** - Cross-origin resource sharing

## Prerequisites

**Option 1: Docker (Recommended)**
- Docker 20.10+
- Docker Compose 2.0+

## Quick Start
### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd demo-project
```

### 2. Configure Settings & Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
cp docker-compose.example.yml docker-compose.yml
cp src/config/settings/example.py src/config/settings/development.py
```

### 3. Build and Start Services

```bash
docker-compose up --build
```

This will:
- Build the Django application container
- Start PostgreSQL database
- Run migrations automatically
- Start the Django development server

The API will be available at `http://localhost:8000/api`

### 4. Stop Services

```bash
docker-compose down
```

### 5. Accessing django shell

Django shell can be accessed using the following command:

```bash
docker-compose exec web python manage.py shell
```

Alternatively

```bash
docker-compose exec web bash
python manage.py shell
```
### Running `manage.py` commands

```bash
docker-compose exec web python manage.py <command>
```

### Running Tests, Coverage, Security

```bash
# Test Only
docker-compose exec web python manage.py test

# Test with Coverage
coverage run --source='.' manage.py test && coverage report

# Check vulnerabilities
safety check

# Security code analysis
bandit -r . -c .bandit
```

## API Endpoints
Available at `/api/swagger/`

## API Usage Examples

### 1. Register a New User

```
POST: http://localhost:8000/api/auth/register/ 
payload:  '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "country": "USA"
  }'
```

### 2. Login and Get Token

```
POST: http://localhost:8000/api/auth/login/ 
payload:  '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Create a User (Super Admin Only)

```bash
method: POST
url: http://localhost:8000/api/users/ 
headers:  "Authorization: Bearer YOUR_ACCESS_TOKEN" \
body: '{
    "username": "country_admin_uk",
    "email": "admin_uk@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "role": "country_admin",
    "country": "UK"
  }'
```

### 4. Create a Project

```bash
method: POST
url: http://localhost:8000/api/projects/ 
headers :  "Authorization: Bearer YOUR_ACCESS_TOKEN" \
body: '{
    "title": "New Infrastructure Project",
    "description": "Building new infrastructure in the region",
    "status": "ACTIVE"
  }'
```

### 5. List Projects

```bash
method: GET
url: http://localhost:8000/api/projects/
header: "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Update a Project

```bash
method: PATCH 
url: http://localhost:8000/api/projects/1/ 
headers :  "Authorization: Bearer YOUR_ACCESS_TOKEN"
body: {"status": "COMPLETED"}
```

### 7. View Audit Logs

```bash
method: GET 
url: http://localhost:8000/api/audit-logs/
header: "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 8. View Recent Audit Logs

```bash
method: GET 
url: http://localhost:8000/api/audit-logs/recent/
header: "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Environment Variables
- `DJANGO_SETTINGS_MODULE`: Settings module (default: config.settings.development)
- `SECRET_KEY` Django secret key (Generated)
- `DEBUG` Debug mode (default: True)
- `ALLOWED_HOSTS` Allowed hosts (default: localhost,127.0.0.1)
- `DB_NAME` Database name (default: project_db)
- `DB_USER` Database user (default: postgres)
- `DB_PASSWORD` Database password (default: postgres)
- `DB_HOST` Database host (default: localhost)
- `DB_PORT` Database port (default: 5432)
- `CORS_ALLOWED_ORIGINS` CORS allowed origins (default: Empty)
