# 🛡️ Anti-Fraud API

Сервис для скоринга и проверки пользователей по Email и IP-адресу. Помогает защитить сайты от автоматических регистраций, ботов и спамеров.

## 💡 Что делает

Принимает пару `email + ip_address`, **параллельно** проверяет их через внешние API и локальные справочники, считает фрод-скор и выносит вердикт:

- **ALLOW** — пользователь безопасен
- **MANUAL_REVIEW** — подозрительный, нужна ручная проверка
- **BLOCK** — мошенник

Все проверки логируются в SQLite для дальнейшей аналитики.

## ✨ Возможности

- ⚡ **Асинхронность** — FastAPI + SQLAlchemy 2.0 async
- 🔄 **Параллельные проверки** — `asyncio.gather` запускает IP и Email проверки одновременно
- 🌍 **IP-обогащение** — страна, город, ISP, флаги прокси/VPN/хостинга через `ip-api.com`
- 📧 **Email-проверка** — локальные списки disposable и free-доменов (без внешних API)
- 🛡️ **Graceful degradation** — если внешний API падает, сервис не падает, а логирует ошибку
- 📊 **Логирование** — каждая проверка сохраняется в SQLite с диагностикой

## 🚀 Быстрый старт

### Требования
- Python 3.12+

### Установка

```bash
# Клонируем
git clone (скопируйте ссылку из кнопки)
cd antifraud-api

# Виртуальное окружение
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Зависимости
pip install -r requirements.txt


Запуск через: uvicorn main:app --reload
доступен http://ip:8000


📖 Пример использования
bash

curl -X POST "http://127.0.0.1:8000/api/v1/check" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@mailinator.com",
    "ip_address": "8.8.8.8"
  }'

# Ответ:

json

{
  "id": 1,
  "email": "user@mailinator.com",
  "ip_address": "8.8.8.8",
  "ip_country": "United States",
  "ip_isp": "Google LLC",
  "ip_is_proxy": false,
  "ip_is_hosting": true,
  "email_domain": "mailinator.com",
  "email_is_disposable": true,
  "fraud_score": 70,
  "verdict": "BLOCK"
}
