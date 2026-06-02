# API Reference — E-Waste Passport

Базовый URL: `https://api.ewaste-passport.io/api/v1`

Интерактивная документация (Swagger UI): `GET /api/docs/`

---

## Аутентификация

Система поддерживает два механизма аутентификации.

**JWT** — для фронтенда и мобильных клиентов.

```http
Authorization: Bearer <access_token>
```

**API Key** — для производителей, интегрирующих регистрацию в ERP.

```http
X-API-Key: <manufacturer_api_key>
```

Публичные эндпоинты (страница паспорта, список пунктов приёма) не требуют аутентификации.

---

## Аутентификация (Auth)

### Получить токены

```http
POST /auth/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secret"
}
```

**Ответ `200 OK`**

```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci..."
}
```

Access token действует **15 минут**, refresh token — **30 дней**.

### Обновить access token

```http
POST /auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJhbGci..."
}
```

**Ответ `200 OK`**

```json
{
  "access": "eyJhbGci..."
}
```

---

## Устройства (Devices)

### Получить паспорт по QR UUID

Публичный эндпоинт. Открывается при сканировании QR-кода.

```http
GET /devices/passport/{qr_uuid}/
```

**Параметры пути**

| Параметр | Тип | Описание |
|---|---|---|
| `qr_uuid` | UUID | Уникальный идентификатор из QR-кода |

**Ответ `200 OK`**

```json
{
  "qr_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "serial_number": "SN-2024-XR15-00421",
  "device": {
    "name": "ProBook X15",
    "category": "laptop",
    "manufacturer": "TechCorp GmbH",
    "eco_index": 72,
    "material_composition": {
      "plastic_g": 420,
      "aluminum_g": 850,
      "lithium_g": 65,
      "copper_g": 120,
      "hazardous": ["lead_solder", "mercury_backlight"]
    }
  },
  "status": "IN_USE",
  "manufactured_at": "2022-03-15",
  "disassembly_guide_url": "https://cdn.ewaste-passport.io/guides/probook-x15.pdf",
  "nearest_collection_points": [
    {
      "id": 42,
      "name": "EcoPoint Mitte",
      "address": "Unter den Linden 12, Berlin",
      "distance_km": 1.4,
      "accepted_categories": ["laptop", "phone", "tablet"]
    }
  ]
}
```

**Ответ `404 Not Found`** — если QR UUID не найден в системе.

---

### Зарегистрировать устройство на себя

Требует JWT-аутентификации владельца.

```http
POST /devices/passport/{qr_uuid}/claim/
Authorization: Bearer <token>
```

**Ответ `200 OK`**

```json
{
  "message": "Device registered to your account.",
  "passport_id": 1091,
  "status": "IN_USE"
}
```

**Ответ `409 Conflict`** — устройство уже зарегистрировано на другого пользователя.

---

### Список устройств текущего пользователя

```http
GET /devices/my/
Authorization: Bearer <token>
```

**Ответ `200 OK`**

```json
{
  "count": 2,
  "results": [
    {
      "qr_uuid": "550e8400-...",
      "serial_number": "SN-2024-XR15-00421",
      "device_name": "ProBook X15",
      "status": "IN_USE",
      "claimed_at": "2024-01-10T14:23:00Z",
      "age_years": 2.1,
      "reminder_active": true
    }
  ]
}
```

---

## Производители (Manufacturers)

Все эндпоинты требуют аутентификации через `X-API-Key` или JWT с ролью `manufacturer`.

### Зарегистрировать модель устройства

```http
POST /manufacturers/devices/
X-API-Key: <api_key>
Content-Type: application/json

{
  "name": "ProBook X15",
  "category": "laptop",
  "material_composition": {
    "plastic_g": 420,
    "aluminum_g": 850,
    "lithium_g": 65,
    "copper_g": 120,
    "hazardous": ["lead_solder"]
  },
  "eco_index": 72
}
```

**Ответ `201 Created`**

```json
{
  "device_id": 884,
  "name": "ProBook X15",
  "category": "laptop"
}
```

---

### Загрузить партию серийных номеров

После регистрации модели загружается партия конкретных экземпляров. В ответ возвращаются QR UUID и публичные ссылки.

```http
POST /manufacturers/devices/{device_id}/batches/
X-API-Key: <api_key>
Content-Type: application/json

{
  "serial_numbers": [
    "SN-2024-XR15-00001",
    "SN-2024-XR15-00002",
    "SN-2024-XR15-00003"
  ],
  "manufactured_at": "2024-06-01"
}
```

**Ответ `201 Created`**

```json
{
  "batch_id": 310,
  "device_id": 884,
  "count": 3,
  "units": [
    {
      "serial_number": "SN-2024-XR15-00001",
      "qr_uuid": "550e8400-e29b-41d4-a716-446655440001",
      "passport_url": "https://ewaste-passport.io/passport/550e8400-e29b-41d4-a716-446655440001"
    },
    {
      "serial_number": "SN-2024-XR15-00002",
      "qr_uuid": "550e8400-e29b-41d4-a716-446655440002",
      "passport_url": "https://ewaste-passport.io/passport/550e8400-e29b-41d4-a716-446655440002"
    },
    {
      "serial_number": "SN-2024-XR15-00003",
      "qr_uuid": "550e8400-e29b-41d4-a716-446655440003",
      "passport_url": "https://ewaste-passport.io/passport/550e8400-e29b-41d4-a716-446655440003"
    }
  ]
}
```

---

### Скачать QR-коды партии (ZIP)

```http
GET /manufacturers/batches/{batch_id}/qr-codes.zip
X-API-Key: <api_key>
```

**Ответ `200 OK`** — ZIP-архив с PNG-файлами QR-кодов, именованными по серийному номеру.

---

### Получить статистику утилизации

```http
GET /manufacturers/analytics/recycling/
X-API-Key: <api_key>
```

**Query параметры**

| Параметр | Тип | Описание |
|---|---|---|
| `from_date` | date | Начало периода (YYYY-MM-DD) |
| `to_date` | date | Конец периода (YYYY-MM-DD) |
| `category` | string | Фильтр по категории устройства |

**Ответ `200 OK`**

```json
{
  "period": {
    "from": "2024-01-01",
    "to": "2024-12-31"
  },
  "total_registered": 15420,
  "total_recycled": 3104,
  "recycling_rate_percent": 20.1,
  "by_category": {
    "laptop": { "registered": 8200, "recycled": 1870 },
    "phone": { "registered": 7220, "recycled": 1234 }
  },
  "by_country": {
    "DE": 1840,
    "FR": 720,
    "PL": 544
  }
}
```

---

## Пункты приёма (Collection Points)

### Поиск ближайших пунктов

Публичный эндпоинт.

```http
GET /collection-points/nearby/
```

**Query параметры**

| Параметр | Тип | Обязательный | Описание |
|---|---|---|---|
| `lat` | float | Да | Широта |
| `lng` | float | Да | Долгота |
| `radius_km` | float | Нет, по умолч. 10 | Радиус поиска |
| `category` | string | Нет | Фильтр по категории устройства |

**Пример запроса**

```http
GET /collection-points/nearby/?lat=52.5200&lng=13.4050&radius_km=5&category=laptop
```

**Ответ `200 OK`**

```json
{
  "count": 3,
  "results": [
    {
      "id": 42,
      "name": "EcoPoint Mitte",
      "address": "Unter den Linden 12, 10117 Berlin",
      "distance_km": 1.4,
      "accepted_categories": ["laptop", "phone", "tablet", "small_appliances"],
      "working_hours": {
        "mon-fri": "09:00-18:00",
        "sat": "10:00-15:00",
        "sun": "closed"
      },
      "is_certified": true,
      "coordinates": {
        "lat": 52.5172,
        "lng": 13.3930
      }
    }
  ]
}
```

---

## Переработчики (Recyclers)

Требует JWT с ролью `recycler`.

### Подтвердить приёмку устройства

```http
POST /recyclers/accept/
Authorization: Bearer <token>
Content-Type: application/json

{
  "qr_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "collection_point_id": 42,
  "notes": "Корпус повреждён, аккумулятор извлечён отдельно"
}
```

**Ответ `200 OK`**

```json
{
  "record_id": 7821,
  "serial_number": "SN-2024-XR15-00421",
  "device_name": "ProBook X15",
  "status_updated_to": "RECYCLED",
  "recycled_at": "2024-11-20T10:45:00Z"
}
```

**Ответ `409 Conflict`** — устройство уже отмечено как утилизированное.

---

## Коды ошибок

| HTTP-статус | Код ошибки | Описание |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Ошибка валидации входных данных; детали в поле `errors` |
| `401` | `UNAUTHORIZED` | Токен отсутствует или недействителен |
| `403` | `FORBIDDEN` | Недостаточно прав для действия |
| `404` | `NOT_FOUND` | Ресурс не найден |
| `409` | `CONFLICT` | Конфликт состояния (устройство уже занято, уже утилизировано и т.п.) |
| `429` | `RATE_LIMITED` | Превышен лимит запросов |
| `500` | `INTERNAL_ERROR` | Внутренняя ошибка сервера |

**Формат ответа при ошибке**

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Serial number already exists in this batch.",
  "errors": {
    "serial_numbers": ["SN-2024-XR15-00001 already registered."]
  }
}
```

---

## Лимиты запросов (Rate Limiting)

| Тип клиента | Лимит |
|---|---|
| Публичные эндпоинты (без авторизации) | 60 запросов / минуту |
| JWT (пользователь) | 300 запросов / минуту |
| API Key (производитель) | 1000 запросов / минуту |

При превышении лимита возвращается `429 Too Many Requests` с заголовком `Retry-After`.

---

## Версионирование

API версионируется через URL (`/api/v1/`). Мажорная версия меняется только при breaking changes. Текущая версия: **v1**.

Устаревшие версии поддерживаются минимум **12 месяцев** после релиза новой.
