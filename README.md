# E-Waste Passport

> Цифровой паспорт электронного устройства — от производства до утилизации.

E-Waste Passport — это платформа, которая присваивает каждому электронному устройству уникальный цифровой паспорт с информацией о составе, инструкциями по разборке и маршрутом корректной утилизации. QR-код на устройстве связывает физический предмет с его цифровой записью на протяжении всего жизненного цикла.

---

## Зачем это нужно

Ежегодно в мире образуется ~60 млн тонн электронного мусора. Около 80% из них утилизируется некорректно — попадает на свалки или в «серые» каналы переработки, где токсичные компоненты (свинец, ртуть, кадмий) загрязняют почву и воду. Проблема не в отсутствии инфраструктуры, а в информационном разрыве между производителями, владельцами и переработчиками.

E-Waste Passport закрывает этот разрыв.

---

## Для кого

| Роль | Что получает |
|---|---|
| **Производитель** | REST API для регистрации партий устройств; автоматическая WEEE-отчётность |
| **Владелец устройства** | Страница паспорта по QR; карта ближайших пунктов приёма; напоминания |
| **Переработчик** | Инструкции по разборке; материальный состав; история приёмки |
| **Регулятор** | Агрегированная аналитика по производителям и регионам |

---

## Стек

- **Backend:** Python 3.12, Django 5, Django REST Framework
- **Frontend:** Vue.js 3, Vite, Pinia
- **База данных:** PostgreSQL 16, PostGIS (геопространственные запросы)
- **Очередь задач:** Celery + Redis (уведомления, отчёты)
- **Хранилище файлов:** S3-совместимое (MinIO для self-hosted, AWS S3 для prod)
- **Контейнеризация:** Docker, Docker Compose

---

## Структура репозитория

```
ewaste-passport/
├── backend/                  # Django-проект
│   ├── config/               # Настройки (settings, urls, wsgi)
│   ├── apps/
│   │   ├── devices/          # Устройства и паспорта
│   │   ├── manufacturers/    # Производители
│   │   ├── recyclers/        # Переработчики и пункты приёма
│   │   ├── users/            # Владельцы устройств
│   │   └── notifications/    # Celery-задачи и уведомления
│   ├── requirements.txt
│   └── manage.py
├── frontend/                 # Vue.js-приложение
│   ├── src/
│   │   ├── views/            # Страницы
│   │   ├── components/       # UI-компоненты
│   │   ├── stores/           # Pinia stores
│   │   └── api/              # API-клиент (axios)
│   └── package.json
├── docs/                     # Документация
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── .editorconfig
└── README.md
```

---

## Быстрый старт

### Требования

- Docker 24+ и Docker Compose v2
- Git

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-org/ewaste-passport.git
cd ewaste-passport
```

### 2. Настроить окружение

```bash
cp .env.example .env
# Отредактируйте .env — как минимум задайте SECRET_KEY и пароль БД
```

### 3. Запустить через Docker Compose

```bash
docker compose up -d
```

Это поднимет: PostgreSQL, Redis, Django-бекенд, Celery-воркер, Vue-фронтенд через Vite dev server.

### 4. Применить миграции и создать суперпользователя

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

### 5. Открыть в браузере

| Сервис | URL |
|---|---|
| Фронтенд | http://localhost:5173 |
| API | http://localhost:8000/api/v1/ |
| Django Admin | http://localhost:8000/admin/ |
| API Docs (Swagger) | http://localhost:8000/api/docs/ |

---

## Разработка без Docker

<details>
<summary>Backend (Django)</summary>

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Убедитесь, что PostgreSQL запущен и задан DATABASE_URL в .env
python manage.py migrate
python manage.py runserver
```

</details>

<details>
<summary>Frontend (Vue.js)</summary>

```bash
cd frontend
npm install
npm run dev
```

</details>

<details>
<summary>Celery (фоновые задачи)</summary>

```bash
cd backend
celery -A config worker -l info
```

</details>

---

## Переменные окружения

Полный список в `.env.example`. Ключевые:

```env
SECRET_KEY=           # Django secret key
DEBUG=True            # False в production
DATABASE_URL=         # postgresql://user:pass@host:5432/dbname
REDIS_URL=            # redis://localhost:6379/0
AWS_S3_BUCKET=        # Для хранения PDF-инструкций
GOOGLE_MAPS_API_KEY=  # Для карты пунктов приёма
```

---

## Тесты

```bash
# Backend
docker compose exec backend python manage.py test

# Frontend
docker compose exec frontend npm run test
```

---

## Лицензия

MIT License. См. [LICENSE](LICENSE).
