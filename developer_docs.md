# Backend Documentation
### Task Manager \u2014 FastAPI Serverless Application

**Version:** 1.0.0  
**Last Updated:** March 18, 2026

## Overview
A serverless application built with FastAPI, deployed on AWS Lambda via Docker container images. Uses Mangum to deploy as serverless, Amazon DynamoDB for persistent data storage, and Redis (via AWS ElastiCache) for caching.

## Tech Stack
* **Framework:** FastAPI
* **Runtime:** Python 3.10
* **Deployment:** AWS Lambda (Docker container)
* **ASGI Adapter:** Mangum
* **Database:** Amazon DynamoDB
* **Cache:** Redis (AWS ElastiCache)
* **Authentication:** JWT + Custom Crypto
* **Infrastructure:** Terraform (IaC)

---

## Project Structure
**Root:** `backend/`

| Path | Description |
| ---- | ----------- |
| `app/api/v1/middleware/` | JWT Authentication middleware \u2014 `get_current_user_id` |
| `app/api/v1/routes/` | FastAPI routers for Auth, Tasks, and Admin |
| `app/config/` | Environment variables loader, database client, and Redis client setup |
| `app/services/` | Core business logic \u2014 AuthService, TaskService, and AdminService |
| `app/utils/` | JWT and cryptographic helper functions |
| `app/main.py` | Application entrypoint and Mangum Lambda handler |
| `terraform/` | AWS infrastructure provisioning \u2014 VPC, ECR, API Gateway, DynamoDB, ElastiCache, IAM, Lambda |
| `Dockerfile` | Lambda container image specification |
| `requirements.txt` | Python dependencies definition |

---

## Database Schema

### Users Table (`USERS_TABLE`)
* **Partition Key:** `user_id` (String \u2014 sequence like "VAH001")
* **Sort Key:** None
* **GSI:** `email-index` (Partition Key: `email`)
* **Attributes:** `user_id`, `username`, `email`, `password`, `role`, `activation_status`

### Tasks Table (`TASKS_TABLE`)
* **Partition Key:** `user_id` (String)
* **Sort Key:** `task_id` (String \u2014 UUID)
* **GSI:** None
* **Attributes:** `user_id`, `task_id`, `title`, `description`, `status` (pending/ongoing/complete), `created_at`

---

## Authentication Flow
1. **Registration (POST `/api/v1/auth/register`)** \u2014 Generates a unique "VAH" `user_id`, encrypts the password using custom cryptographic logic (`crypto.py`), and stores it with a default "user" role and "active" status in DynamoDB.
2. **Login (POST `/api/v1/auth/login`)** \u2014 Queries DynamoDB using the `email-index` GSI, validates the decrypted password, and returns a signed JWT via a 'Bearer' token on success.
3. **Protected Routes** \u2014 The `get_current_user_id` middleware intercepts requests, extracts the Bearer token from the authorization header, validates it using the `JWT_SECRET`, and injects the `user_id` into route parameters.

---

## Caching Strategy
* **Key Format:** `tasks:{user_id}`
* **TTL:** 300 seconds
* **Used For:** `GET /api/v1/tasks/fetch-task`
* **Invalidation Trigger:** Aggressively invalidated upon task creation, update, or deletion operations.
* **Resiliency Fallback:** Redis connection issues immediately flip the `redis_disabled` flag to `True` globally to prevent continuous request latency. Redis is completely bypassed locally when `ENVIRONMENT="development"`.

---

## Endpoints

### Authentication
* **POST `/api/v1/auth/register`** (Public) - Register a new user (`username`, `email`, `password`, `role`, `activation_status`). Returns the created user object.
* **POST `/api/v1/auth/login`** (Public) - Log in using `email` and `password`. Returns `{ "access_token": "...", "token_type": "bearer" }`.
* **GET `/api/v1/auth/user`** (Protected) - Get current authenticated user info alongside detailed task statistics (counts per status).

### Tasks
* **POST `/api/v1/tasks/create-task`** (Protected) - Create a new assigned task (`title`, `description`). Returns generated the task instance.
* **GET `/api/v1/tasks/fetch-task`** (Protected) - Fetch all tasks for the logged in user. Actively cached via Redis.
* **PUT `/api/v1/tasks/update-task/{task_id}`** (Protected) - Update specific task workflow `status` (pending/ongoing/complete).
* **DELETE `/api/v1/tasks/delete-task/{task_id}`** (Protected) - Delete task instance by ID.

### Admin
* **GET `/api/v1/admin/users`** (Protected - Admin Only) - List all registered system users.
* **PUT `/api/v1/admin/update-user/{user_id}`** (Protected - Admin Only) - Update administrative properties for a user (`username`, `email`, `password`, `activation_status`).

---

## Environment Variables
* `AWS_REGION` - Target AWS region (e.g. `us-east-1`)
* `USERS_TABLE` - Name of DynamoDB Users table
* `TASKS_TABLE` - Name of DynamoDB Tasks table
* `JWT_SECRET` - Key used to securely sign JWTs
* `PASS_SECRET_KEY` - Key for encrypting passwords
* `REDIS_HOST` - Endpoint for the ElastiCache cluster
* `REDIS_PORT` - Connection port for Redis (`6379`)
* `ENVIRONMENT` - Execution context (e.g. `development` to bypass Redis timeouts)

---

## Local Setup
1. Create and activate a Virtual Environment: `python -m venv venv && source venv/bin/activate` (or equivalent Windows script `venv\Scripts\activate`)
2. Install Python dependencies: `pip install -r requirements.txt`
3. Configure `.env` using required variables (ensure `ENVIRONMENT=development` is set to safely ignore cloud-only cache behavior).
4. Run the Uvicorn development server: `uvicorn app.main:app --reload`

---

## Deployment Strategy
1. Authenticate local AWS configuration with the AWS CLI.
2. In the `terraform/` directory, run `terraform init` and `terraform apply` to provision AWS environment infrastructure (VPC, ECR, API Gateway, DynamoDB, ElastiCache, IAM logic).
3. Build the Docker image specifically matching AWS Lambda `python:3.10` foundations and push it securely to the provisioned ECR registry.
4. Update the AWS Lambda configuration natively or inside Terraform targeting newly updated ECR Image versions.
