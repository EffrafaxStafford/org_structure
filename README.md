# org_structure

API организационной структуры на `Django REST Framework`.

Проект реализует:
- создание подразделений
- создание сотрудников внутри подразделений
- получение подразделения с сотрудниками и поддеревом дочерних подразделений
- перенос подразделения
- удаление подразделения в режимах `cascade` и `reassign`

## Стек

- Python 3.9
- Django 4.2
- Django REST Framework
- PostgreSQL
- Docker Compose
- pytest

## Структура проекта

- `org_structure/config/` — настройки Django
- `org_structure/department/` — модели, сериализаторы, вьюхи и маршруты API
- `org_structure/tests/` — pytest-тесты
- `docker-compose.yml` — запуск приложения и PostgreSQL
- `org_structure/Dockerfile` — образ backend-сервиса


## Запуск через Docker Compose

1. Убедиться, что установлен Docker и Docker Compose.
2. Создать файл `.env`:

```bash
cp .env.example .env
```

3. Запустить контейнеры:

```bash
docker compose up --build
```

После запуска API будет доступен по адресу [http://localhost:8000](http://localhost:8000)

При первом запуске в базу автоматически загружаются демо-данные из `org_structure/department/fixtures/demo_data.json`.

Если нужно полностью пересоздать базу и заново загрузить фикстуру:

```bash
docker compose down -v
docker compose up --build
```

## Тесты

Запуск тестов внутри Docker-контейнера:

```bash
docker compose exec backend pytest
```

## API

### Создать подразделение

`POST /departments/`

Пример body:

```json
{
  "name": "Backend",
  "parent": null
}
```

### Создать сотрудника в подразделении

`POST /departments/{id}/employees/`

Пример body:

```json
{
  "full_name": "Ivan Ivanov",
  "position": "Developer",
  "hired_at": "2026-05-19"
}
```

### Получить подразделение с деревом

`GET /departments/{id}/?depth=2&include_employees=true`

### Обновить подразделение

`PATCH /departments/{id}/`

Пример body:

```json
{
  "name": "Platform",
  "parent": 1
}
```

### Удалить подразделение каскадно

`DELETE /departments/{id}/?mode=cascade`

### Удалить подразделение с переносом сотрудников и дочерних подразделений

`DELETE /departments/{id}/?mode=reassign&reassign_to_department_id=2`

## Дополнительно

- Максимальная глубина `depth` — `5`
- При `include_employees=false` сотрудники не включаются в ответ
- Названия подразделений уникальны в рамках одного `parent`
- Нельзя сделать подразделение родителем самого себя
- Нельзя перенести подразделение внутрь собственного поддерева
