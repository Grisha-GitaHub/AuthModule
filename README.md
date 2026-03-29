# Система аутентификации и авторизации

## Обзор

Данное приложение представляет собой систему аутентификации и авторизации с разграничением прав доступа на основе ролей (RBAC - Role-Based Access Control).

**Основные возможности:**
- ✅ Регистрация и вход пользователей
- ✅ JWT аутентификация (RS256) с поддержкой cookie
- ✅ Система ролей и прав доступа (RBAC)
- ✅ Soft delete пользователей
- ✅ Mock бизнес-объекты с проверкой прав
- ✅ API для администратора

---

## Схема базы данных

### Таблицы

#### 1. `user` — Пользователи
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| username | VARCHAR(50) | Имя пользователя |
| userfamily | VARCHAR(50) | Фамилия |
| userpatronic | VARCHAR(50) | Отчество |
| email | VARCHAR(100) | Email (уникальный) |
| hashed_password | VARCHAR(255) | Хеш пароля (bcrypt) |
| is_active | BOOLEAN | Статус аккаунта (True/False) |

#### 2. `role` — Роли
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| name | VARCHAR(50) | Название роли (уникальное) |
| description | VARCHAR(255) | Описание роли |

#### 3. `permission` — Права
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| name | VARCHAR(50) | Название права (уникальное) |
| description | VARCHAR(255) | Описание права |

#### 4. `user_role` — Связь пользователей и ролей (многие-ко-многим)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| user_id | INTEGER | Внешний ключ на user.id |
| role_id | INTEGER | Внешний ключ на role.id |
| granted_at | DATETIME | Дата назначения роли |

#### 5. `role_permission` — Связь ролей и прав (многие-ко-многим)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| role_id | INTEGER | Внешний ключ на role.id |
| permission_id | INTEGER | Внешний ключ на permission.id |

#### 6. `token_blacklist` — Чёрный список токенов
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| token | VARCHAR(500) | JWT токен (уникальный) |
| expires_at | DATETIME | Время истечения токена |
| blacklisted_at | DATETIME | Дата добавления в blacklist |

---

## Система разграничения прав доступа

### Архитектура

Система использует **RBAC (Role-Based Access Control)** — модель разграничения прав доступа на основе ролей.

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   User      │──────│  UserRoles   │──────│    Role     │
│  (user)     │      │ (user_role)  │      │  (role)     │
└─────────────┘      └──────────────┘      └─────────────┘
                                                │
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │RolePermission│
                                         │(role_permissi│
                                         └──────────────┘
                                                │
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │ Permission  │
                                         │(permission) │
                                         └─────────────┘
```

### Роли

| Роль | Описание | Права |
|------|----------|-------|
| **admin** | Администратор системы | Полный доступ ко всем ресурсам (create, read, update, delete) |
| **manager** | Менеджер | Чтение и обновление ресурсов |
| **user** | Обычный пользователь | Только чтение публичных и внутренних ресурсов |

### Права (Permissions)

| Право | Описание |
|-------|----------|
| **create** | Создание новых объектов |
| **read** | Чтение/просмотр объектов |
| **update** | Обновление существующих объектов |
| **delete** | Удаление объектов |

### Уровни доступа к бизнес-объектам

| Уровень | Описание |
|---------|----------|
| **public** | Доступно всем авторизованным пользователям |
| **internal** | Доступно пользователям с правом read |
| **private** | Доступно только пользователям с соответствующими правами |

---

## Правила доступа

### Алгоритм проверки доступа

1. **Идентификация пользователя**
   - Проверка JWT токена в заголовке `Authorization: Bearer <token>` или в cookie
   - Если токен отсутствует или невалиден → **401 Unauthorized**

2. **Проверка статуса аккаунта**
   - Проверка поля `is_active` у пользователя
   - Если `is_active=False` → **403 Forbidden** (аккаунт деактивирован)

3. **Проверка прав доступа**
   - Получение ролей пользователя из таблицы `user_role`
   - Получение прав ролей из таблицы `role_permission`
   - Если у пользователя нет требуемого права → **403 Forbidden**

4. **Проверка доступа к ресурсу**
   - Проверка уровня доступа ресурса (public/internal/private)
   - Если доступ запрещён → **403 Forbidden**

### Коды ошибок

| Код | Описание |
|-----|----------|
| **401 Unauthorized** | Пользователь не авторизован (токен отсутствует или невалиден) |
| **403 Forbidden** | Пользователь авторизован, но не имеет прав для доступа к ресурсу |
| **404 Not Found** | Ресурс не найден |
| **409 Conflict** | Конфликт данных (например, email уже занят) |
| **422 Unprocessable Entity** | Ошибка валидации данных |

---

## API Endpoints

### Аутентификация (`/api/auth`)

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| POST | `/login` | Вход (получение токена) | Public |
| GET | `/me` | Данные текущего пользователя | Авторизованным |
| POST | `/logout` | Выход из системы | Авторизованным |

### Пользователи (`/api/users`)

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| POST | `/register` | Регистрация нового пользователя | Public |
| GET | `/me` | Профиль текущего пользователя | Авторизованным |
| PATCH | `/update_me` | Обновление профиля | Авторизованным |
| DELETE | `/me` | Удаление аккаунта (soft delete) | Авторизованным |

### Токены (`/api/tokens`)

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| POST | `/logout` | Выход из системы (удаление cookie) | Авторизованным |
| POST | `/refresh` | Обновление токена | Авторизованным |

### Администрирование (`/api/admin`)

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/roles` | Список всех ролей | Admin |
| POST | `/roles` | Создание роли | Admin |
| GET | `/permissions` | Список всех прав | Admin |
| POST | `/permissions` | Создание права | Admin |
| POST | `/roles/{role_id}/permissions/{permission_id}` | Назначить право роли | Admin |
| POST | `/users/{user_id}/roles/{role_id}` | Назначить роль пользователю | Admin |
| GET | `/users/{user_id}/roles` | Роли пользователя | Admin |

### Бизнес-объекты (`/api/business`)

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/projects` | Список проектов | read |
| GET | `/projects/{id}` | Проект по ID | read |
| POST | `/projects` | Создание проекта | create |
| GET | `/documents` | Список документов | read |
| GET | `/documents/{id}` | Документ по ID | read |
| GET | `/reports` | Список отчётов | read |

---

## Тестовые данные

При первом запуске приложение автоматически создаёт:

### Роли
- **admin** — Администратор
- **manager** — Менеджер
- **user** — Пользователь

### Права
- **create** — Создание
- **read** — Чтение
- **update** — Обновление
- **delete** — Удаление

### Назначения прав ролям
- **admin**: create, read, update, delete (все права)
- **manager**: read, update
- **user**: read

### Учётная запись администратора

После запуска приложения выполните скрипт для создания администратора:

```bash
cd fastapi-app
python create_admin.py
```

Или зарегистрируйтесь через API первым пользователем — роль admin будет назначена автоматически.

| Параметр | Значение |
|----------|----------|
| **ID** | 1 |
| **Email** | `admin@admin.com` |
| **Пароль** | `admin123` |
| **Роль** | `admin` (полные права) |

> **Важно:** После первого входа рекомендуется сменить пароль администратора!

---

## Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск сервера

```bash
cd fastapi-app
python main.py
```

Сервер запустится на `http://localhost:8000`

### Swagger UI

Документация API доступна по адресу: **http://localhost:8000/docs**

---

## Примеры использования

### 1. Создание администратора

```bash
cd fastapi-app
python create_admin.py
```

### 2. Вход администратора

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@admin.com",
    "password": "admin123"
  }'
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "email": "admin@admin.com",
  "message": "Токен также установлен в cookie"
}
```

> Токен автоматически сохраняется в httpOnly cookie для удобства работы через Swagger UI.

### 3. Регистрация пользователя

```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ivan",
    "userfamily": "Ivanov",
    "userpatronic": "Ivanovich",
    "email": "ivan@example.com",
    "password": "password123",
    "check_password": "password123"
  }'
```

### 4. Вход

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ivan@example.com",
    "password": "password123"
  }'
```

### 5. Получение профиля

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <your_token>"
```

### 6. Получение списка проектов

```bash
curl -X GET http://localhost:8000/api/business/projects \
  -H "Authorization: Bearer <your_token>"
```

### 7. Назначение роли пользователю (требуется admin)

```bash
curl -X POST http://localhost:8000/api/admin/users/{user_id}/roles/{role_id} \
  -H "Authorization: Bearer <admin_token>"
```

---

## Безопасность

### JWT токены

- **Алгоритм**: RS256 (RSA с хешированием SHA-256)
- **Время жизни**: 5 минут
- **Тип**: Bearer
- **Хранение**: Authorization header или httpOnly cookie

### Хеширование паролей

- **Алгоритм**: bcrypt
- **Соль**: Автоматически генерируется для каждого пароля

### Cookie аутентификация

При login токен устанавливается в cookie с параметрами:
- `httponly=True` — недоступно для JavaScript (защита от XSS)
- `samesite="lax"` — защита от CSRF
- `secure=False` — для HTTPS установите True

### Logout

При выходе из системы cookie удаляется. Для полной реализации токен также добавляется в чёрный список (`token_blacklist`).

---

## Структура проекта

```
fastapi-app/
├── main.py                 # Точка входа
├── create_admin.py         # Скрипт создания администратора
├── api/
│   ├── __init__.py         # Роуты
│   ├── dependencies.py     # Dependencies для проверки прав
│   ├── admin.py            # API администратора
│   ├── business.py         # Mock бизнес-объекты
│   └── auth/
│       ├── jwt_auth.py     # Аутентификация (login, me)
│       └── tokens.py       # Токены (logout, refresh)
├── core/
│   ├── config.py           # Настройки приложения
│   └── models/
│       ├── __init__.py     # Экспорт моделей
│       ├── base.py         # Базовый класс SQLAlchemy
│       ├── db_helper.py    # Помощник БД
│       ├── user.py         # Модель User
│       ├── role.py         # Модель Role
│       ├── permission.py   # Модель Permission
│       ├── resource.py     # Модель Resource
│       ├── user_role.py    # Модель UserRole
│       ├── role_permission.py
│       ├── token_blacklist.py
│       ├── access_control.py # Функции проверки прав
│       └── seed.py         # Инициализация данных
├── utils/
│   └── case_converter.py   # Конвертеры имён
└── certs/
    ├── private.pem         # Приватный ключ RSA
    └── public.pem          # Публичный ключ RSA
```

---

## Тестирование

Для комплексного тестирования API выполните:

```bash
cd fastapi-app
test_api.bat
```

Скрипт проверяет:
1. Создание администратора
2. Вход и получение токена
3. Получение профиля
4. Список ролей, прав, ресурсов
5. Регистрацию пользователя
6. Доступ к бизнес-объектам
7. Назначение ролей
8. Logout
