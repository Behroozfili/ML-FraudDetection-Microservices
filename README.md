# ML Fraud Detection — Microservices Platform

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Kubernetes-K8s-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white"/>
  <img src="https://img.shields.io/badge/gRPC-Protobuf-244C5A?style=for-the-badge&logo=grpc&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/Prometheus-Grafana-E6522C?style=for-the-badge&logo=prometheus&logoColor=white"/>
  <img src="https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=for-the-badge&logo=github-actions&logoColor=white"/>
</p>

> A **production-ready microservices platform** for real-time fraud detection using machine learning. Each domain concern is isolated into its own service with independent deployment, API contracts enforced via gRPC/Protobuf, Kubernetes orchestration across dev and production overlays, and full observability with Prometheus + Grafana.

---

## System Architecture

```
                         ┌─────────────────┐
   Client Request ──────►│   API Gateway   │
                         └────────┬────────┘
                                  │ HTTP / gRPC
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
     ┌──────────────┐   ┌──────────────────┐  ┌──────────────────┐
     │ User Service │   │Transaction Service│  │Notification Svc  │
     │  FastAPI+JWT │   │  gRPC (tx.proto) │  │  Email / Webhook │
     │  PostgreSQL  │   └────────┬─────────┘  └──────────────────┘
     │  Alembic     │            │
     └──────────────┘            ▼
                        ┌─────────────────┐
                        │  Fraud ML Svc   │
                        │  Inference API  │
                        └─────────────────┘
                                  │
             ┌────────────────────┴──────────────────┐
             ▼                                       ▼
     Prometheus (metrics)                  Grafana (dashboards)
```

---

## Services

### User Service
Handles authentication, registration, and user profile management.

| Feature | Implementation |
|---|---|
| REST API | FastAPI + Uvicorn |
| Auth | JWT (Bearer tokens) + bcrypt passwords |
| ORM | SQLAlchemy + Alembic migrations |
| Database | PostgreSQL |
| Tests | pytest with DB integration tests |

### Transaction Service
Processes incoming financial transactions and invokes the fraud ML service.

- gRPC interface defined in `libs/api-contracts/transaction.proto`
- Kubernetes `Deployment` + `Service` manifests
- Production resource limits patched via Kustomize overlay

### Fraud ML Service
Hosts the trained fraud detection model behind a lightweight inference API.

- Dedicated `Dockerfile` for model serving
- Kubernetes `Deployment` + `Service`
- Model loading from mounted volume or model registry

### API Gateway
Single entry point for all client traffic — routes requests to the appropriate downstream service.

- HTTP reverse proxy
- Kubernetes `Ingress` + `Service`
- Rate limiting & auth header forwarding

### Notification Service
Fires alerts (email/webhook) when a transaction is flagged as fraudulent.

- Kubernetes `Deployment` + `Service`
- Configurable notification backends

---

## Project Structure

```
ML-FraudDetection-Microservices/
├── user-service/
│   ├── src/
│   │   ├── main.py           # FastAPI app, JWT auth routes
│   │   ├── models.py         # SQLAlchemy + Pydantic models
│   │   ├── crud.py           # DB operations
│   │   ├── database.py       # Engine + session factory
│   │   └── config.py         # Settings
│   ├── alembic/              # Database migrations
│   ├── tests/                # pytest test suite
│   ├── kubernetes/           # K8s Deployment + Service YAMLs
│   ├── docker-compose.dev.yml
│   ├── Dockerfile
│   └── requirements.txt
├── fraud-ml-service/
│   ├── kubernetes/
│   ├── Dockerfile
│   └── requirements.txt
├── transaction-service/
│   └── kubernetes/
├── notification-service/
│   └── kubernetes/
├── gateway/
│   └── kubernetes/           # Deployment + Service + Ingress
├── libs/
│   ├── api-contracts/
│   │   ├── transaction.proto # gRPC transaction contract
│   │   └── user.proto        # gRPC user contract
│   └── common-utils/         # Shared utilities
├── kubernetes-platform/
│   ├── overlays/
│   │   ├── development/      # Kustomize dev overlay
│   │   └── production/       # Kustomize prod overlay (resource limits)
│   ├── prometheus/           # Prometheus Helm values
│   └── grafana/              # Grafana Helm values
├── .github/workflows/
│   ├── ci-user-service.yml           # CI for user-service
│   ├── ci-service-template.yml       # Reusable CI template
│   ├── cd-deploy-staging.yml         # CD → staging environment
│   └── cd-deploy-production.yml      # CD → production environment
└── README.md
```

---

## API Contracts (gRPC / Protobuf)

Shared contracts in `libs/api-contracts/`:

```protobuf
// transaction.proto (excerpt)
service TransactionService {
  rpc ProcessTransaction (TransactionRequest) returns (TransactionResponse);
}

message TransactionRequest {
  string transaction_id = 1;
  string customer_id    = 2;
  double amount         = 3;
  string currency       = 4;
}
```

---

## Kubernetes — Environment Overlays

The platform uses **Kustomize** for environment-specific configuration:

```bash
# Deploy to development
kubectl apply -k kubernetes-platform/overlays/development/

# Deploy to production
kubectl apply -k kubernetes-platform/overlays/production/
```

Production overlay applies:
- Resource requests/limits for transaction-service
- Replica count patches for user-service

---

## Observability

### Prometheus
Deployed via Helm with custom `values.yaml`. Scrapes metrics from all services automatically via pod annotations.

### Grafana
Pre-configured with Prometheus as data source. Dashboards track:
- Request rate and latency per service
- Fraud detection rate and false positive rate
- User registration / login throughput

```bash
# Install Prometheus
helm upgrade --install prometheus prometheus-community/prometheus \
  -f kubernetes-platform/prometheus/values.yaml

# Install Grafana
helm upgrade --install grafana grafana/grafana \
  -f kubernetes-platform/grafana/values.yaml
```

---

## CI/CD

| Workflow | Trigger | Action |
|---|---|---|
| `ci-user-service.yml` | PR to `main` | Lint, test, build Docker image |
| `ci-service-template.yml` | Reusable | Shared CI steps for all services |
| `cd-deploy-staging.yml` | Push to `develop` | Deploy to staging namespace |
| `cd-deploy-production.yml` | Push to `main` | Deploy to production namespace |

---

## Getting Started

### Prerequisites

- Docker + Docker Compose
- `kubectl` + `kustomize`
- Helm 3
- PostgreSQL (or use Docker Compose)

### Local Development (User Service)

```bash
cd user-service
docker-compose -f docker-compose.dev.yml up --build

# Run tests
pytest tests/ -v
```

### Run Migrations

```bash
cd user-service
alembic upgrade head
```

### Deploy to Kubernetes

```bash
# Apply all platform components
kubectl apply -k kubernetes-platform/overlays/development/

# Apply individual services
kubectl apply -f user-service/kubernetes/
kubectl apply -f fraud-ml-service/kubernetes/
kubectl apply -f gateway/kubernetes/
```

---

## License

MIT
