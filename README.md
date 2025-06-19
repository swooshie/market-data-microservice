# 📈 Market Data Microservice

A microservice for polling stock prices, computing moving averages, and storing market data using FastAPI, PostgreSQL, Kafka, Redis, and Finnhub API.

---

## 🧰 Tech Stack

- **FastAPI** – for building the RESTful APIs
- **PostgreSQL** – for storing raw and processed stock data
- **Redis** – for caching the latest stock prices
- **Kafka** – for producing and consuming price events
- **finnhub-python** – for fetching live market data
- **Docker & Docker Compose** – for containerization
- **Pytest** – for testing both sync and async routes
- **SlowAPI** – for rate limiting
- **GitHub Actions** – for CI testing and linting

---

## ⚙️ Setup Instructions

### 🔧 Prerequisites

- Docker & Docker Compose
- Python 3.12 (only if testing locally without Docker)
- Finnhub API Key (free key from [https://finnhub.io](https://finnhub.io))

---

### 🚀 Running the Microservice

1. **Clone the repository:**

```bash
git clone https://github.com/swooshie/market-data-microservice.git
cd market-data-microservice
```

2. Add your API key to environment and also to the docker file:
```bash
export FINNHUB_API_KEY=your_actual_api_key
```
If FINNHUB_API_KEY is not set, a fallback demo key will be used.

3.	Run all services via Docker after change the POSTGRES user and password in these lines:
```docker
environment:
      DATABASE_URL: postgresql+asyncpg://<db>:<user>@<pwd>:5432/market_data
```

```
environment:
      POSTGRES_DB: <db>
      POSTGRES_USER: <user>
      POSTGRES_PASSWORD: <pwd>
```
```bash
docker-compose up --build
```

4.	Access the API at:
```bash
http://localhost:8000/docs
```

5. Check Admirer
```
http://localhost:8080/
```
to check if the appropriate get request data was reflected in the postgres database

**Architecture Overview**

***Components***

| Component       | Role                                                              |
|----------------|-------------------------------------------------------------------|
| FastAPI         | Handles API endpoints and request routing                         |
| PostgreSQL      | Persists raw prices and computed moving averages                  |
| Redis           | Caches latest prices for quick retrieval                          |
| Kafka           | Publishes and consumes stock data for async processing            |
| finnhub-python  | Fetches real-time data from the Finnhub stock market API          |

**Project Structure**
```bash
market-data-microservice/
├── app/
│   ├── api/                  # API endpoints
│   ├── core/                 # Logging, settings, cache, limiter
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Schemas for API request and response objects
│   ├── services/             # Business logic and provider integrations
│   └── main.py               # App initialization
├── postman/                  # Postman api and testing json
├── scripts/                  # Utility scripts (DB init, consumers)
├── tests/                    # Pytest unit/integration tests
├── docker-compose.yml        # Docker services
├── Dockerfile                # Dockerfile
├── requirements.txt          # Python dependencies
├── .github/workflows/ci.yml  # GitHub Actions CI
└── README.md
```

Swagger UI is auto-generated at:
```
http://localhost:8000/docs
```

**GET /prices/latest**

Fetches the latest stock price from the Finnhub API.

Query Parameters:
- symbol (str): Stock symbol (e.g., AAPL)

Sample request

```
GET /prices/latest?symbol=AAPL
```

```json
{
  "symbol": "AAPL",
  "price": 151.23,
  "timestamp": "2025-06-19T15:10:00Z",
  "provider": "Finnhub"
}
```

**POST /prices/poll**

Creates a polling job to repeatedly fetch stock data for a set of symbols

Request Body:

```json
{
  "symbols": ["AAPL", "MSFT"],
  "interval": 60,
  "provider": "finnhub"
}
```

Responde Body:

```json
{
  "job_id": "poll_ab12cd",
  "status": "accepted",
  "config": {
    "symbols": ["AAPL", "MSFT"],
    "interval": 60,
    "provider": "finnhub"
  }
}
```

**Testing**

Run pytest

```bash
pytest -q
```
Includes both sync and async tests for:
- API endpoints
- Moving average calculation logic


**Finnhub Integration**

We use the finnhub-python client to get live data.

Sample: Fetching latest quote

```python
import finnhub

client = finnhub.Client(api_key="your_api_key")
quote = client.quote("AAPL")
price = quote["c"]  # current price
```

This data is used inside AlphaVantageProvider (which was earlier used for dummy values) replacement class to fetch real-time values.

GitHub Actions CI

Defined in .github/workflows/ci.yml and includes:
- Installing dependencies
- Running pytest
- Building the Docker image