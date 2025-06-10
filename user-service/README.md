# User Service

User management service for the financial fraud detection system. This service includes authentication, user management, and CRUD APIs.

## Features

- ✅ User registration and login
- ✅ JWT Authentication
- ✅ User CRUD operations
- ✅ Data validation
- ✅ Password security with bcrypt
- ✅ API documented with FastAPI
- ✅ Ready for Kubernetes deployment
- ✅ Unit and integration tests

## Architecture
Use code with caution.
Markdown
user-service/
├── src/
│ ├── main.py # Main FastAPI application
│ ├── models.py # SQLAlchemy and Pydantic models
│ ├── database.py # Database settings
│ ├── crud.py # CRUD operations
│ └── config.py # Service settings
├── tests/ # Tests
├── kubernetes/ # Kubernetes files
├── config/ # Configuration files
├── Dockerfile
├── requirements.txt
└── README.md
## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Log in a user

### User Management
- `GET /users/me` - Get current user information
- `GET /users` - Get a list of users
- `GET /users/{user_id}` - Get specific user information
- `PUT /users/{user_id}` - Update user information
- `DELETE /users/{user_id}` - Delete a user

### Service Health
- `GET /health` - Check service health

## Local Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (or SQLite for development)
- Docker (optional)

### Install Dependencies
```bash
pip install -r requirements.txt
Use code with caution.
Set Environment Variables
Create a .env file in the user-service/src/ directory (if your config.py is set up to read from it, e.g., using pydantic-settings):
# .env (example, place in user-service/src/ or ensure your config.py can find it)
DATABASE_URL=postgresql://user:password@localhost:5432/userdb
SECRET_KEY=your-secret-key-here # Change this!
ENVIRONMENT=development
DEBUG=true
PORT=8000
LOG_LEVEL=DEBUG
# CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000 # Example for local frontend
Use code with caution.
Bash
Alternatively, set these as system environment variables.
Running the Service
# Run in development mode (from user-service/ directory)
uvicorn src.main:app --reload --port 8000

# Or using Docker (from user-service/ directory)
docker build -t user-service .
docker run -p 8000:8000 --env-file src/.env user-service # Example if using .env in src/
# Or pass environment variables directly:
# docker run -p 8000:8000 \
#   -e DATABASE_URL="postgresql://user:password@host.docker.internal:5432/userdb" \
#   -e SECRET_KEY="your-secret-key-here" \
#   -e ENVIRONMENT="development" \
#   user-service
Use code with caution.
Bash
Note: For Docker to connect to a PostgreSQL instance running on your host machine (not in another Docker container defined in the same docker-compose network), you might need to use host.docker.internal (on Docker Desktop for Mac/Windows) or your host's IP address for DATABASE_URL instead of localhost. If PostgreSQL is running in another container (e.g., via docker-compose.dev.yml), use the service name (e.g., postgres).
Running Tests
# From the user-service/ directory
pytest tests/ -v --cov=src
Use code with caution.
Bash
Kubernetes Deployment
1. Create Secrets
Before deploying, ensure you have Kubernetes secrets for sensitive data.
# Example: Create secrets for database URL and JWT secret key
kubectl create secret generic user-service-secrets \
  --from-literal=database-url="postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@YOUR_POSTGRES_SERVICE_HOST:5432/YOUR_DB_NAME" \
  --from-literal=secret-key="YOUR_STRONG_JWT_SECRET_KEY" \
  --namespace <your-namespace> # Specify namespace if not default
Use code with caution.
Bash
(Refer to your user-service/kubernetes/deployment.yaml for the exact secret name and keys expected.)
2. Apply Manifests
# From the root of the project or user-service/ directory
kubectl apply -f user-service/kubernetes/
Use code with caution.
Bash
3. Check Status
kubectl get pods -l app=user-service --namespace <your-namespace>
kubectl logs -l app=user-service --namespace <your-namespace> -c user-service # -c to specify container if multiple
Use code with caution.
Bash
Production Environment Settings
Important Environment Variables
DATABASE_URL: Database connection URL
SECRET_KEY: Secret key for JWT (must be strong and kept secret)
ENVIRONMENT: production
DEBUG: false
LOG_LEVEL: INFO
CORS_ORIGINS: Comma-separated list of allowed origins (e.g., https://yourdomain.com,https://www.yourdomain.com)
Security
Passwords are hashed with bcrypt
JWT tokens for authentication
Input validation with Pydantic
CORS access restriction
Example Usage
Register User
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  }'
Use code with caution.
Bash
Login User
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
Use code with caution.
Bash
Access Protected APIs
Replace YOUR_JWT_TOKEN with the access_token received from login.
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
Use code with caution.
Bash
Contributing
Fork the project
Create your feature branch (git checkout -b feature/new-feature)
Commit your changes (git commit -am 'Add new feature')
Push to the branch (git push origin feature/new-feature)
Create a new Pull Request
License
This project is licensed under the MIT License.
Support
For bug reports or feature requests, please create an issue on the GitHub repository.
**Key changes and considerations in the English version:**

*   All titles, descriptions, and comments are translated.
*   **Environment Variables for Local Setup:** I clarified that the `.env` file is typically placed where `config.py` can find it (often `user-service/src/` if using `pydantic-settings` with default `.env` loading) or that system environment variables can be used.
*   **Docker Run Command:** Added an example of using `--env-file` and also how to pass environment variables directly. Also added a note about `DATABASE_URL` when connecting from Docker to a host-running database.
*   **Kubernetes Secrets:** Emphasized replacing placeholder values with actual secure values and specifying the namespace. Also mentioned referring to the `deployment.yaml` for expected secret names/keys.
*   **Kubernetes Check Status:** Added namespace and container name specification for clarity.
*   **CORS_ORIGINS for Production:** Added an example of what this might look like.
*   **Example Usage:** Clarified that `YOUR_JWT_TOKEN` needs to be replaced.

This English README should be very helpful for anyone looking at your `user-service`. Remember to `git add README.md`, `git commit -m "Translate user-service README to English"`, and `git push` after you've saved this content in your `user-service/README.md` file.
