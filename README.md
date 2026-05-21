# Organization Structure API

Тестовое задание Django REST Framework.

## Стек

- Django
- Django REST Framework
- PostgreSQL
- Redis
- Nginx
- Docker / docker-compose

## API

### Departments
- `POST /api/v1/departments/`
- `GET /api/v1/departments/{id}/`
- `PATCH /api/v1/departments/{id}/`
- `DELETE /api/v1/departments/{id}/`

### Employees
- `POST /api/v1/departments/{id}/employees/`

## Переменные окружения

Для запуска проекта нужен файл `.env` в корне проекта, рядом с `docker-compose.yaml`.

Пример:

```env
SECRET_KEY=your-secret-key
POSTGRES_DB=organization_db
POSTGRES_USER=organization_user
POSTGRES_PASSWORD=organization_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
```

### 1. Собрать и запустить контейнеры
```bash
docker compose up --build
```

### 2. Применить миграции
```bash
docker compose exec web python manage.py migrate
```


## Запуск тестов

Все тесты:

```bash
docker compose exec web pytest
```

Тесты departments:

```bash
docker compose exec web pytest departments/tests/test_department_api.py
```

Тесты employees:

```bash
docker compose exec web pytest employees/tests/test_employee_api.py
```

