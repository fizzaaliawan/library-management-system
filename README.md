# Library Management System (LMS)

This repository contains a containerized, production-grade Library Management System (LMS) built with modern Clean Architecture, SOLID design principles, and scalable software design patterns.


---

## About

* **Git Workflow (PR-Based Flow)**: Automated lints (Ruff) + tests (Pytest) run on every PR.
* **Containerization**: Entire app stack + PostgreSQL runs via a single Compose command; database data persists in Postgres volumes.
* **Database Schema + Migrations + Seeds**: Shares unified database schemas, tracks versioning using Alembic migrations, and initializes with **17 books** across 8 subjects via an SQLAlchemy ORM.
* **CI/CD Pipeline**: Merges to `main` / `staging` build container images, run checks, and push them to **GHCR (GitHub Container Registry)**.
* **Server Run**: Images are pulled and run on your own EC2 instance using a production compose file.
* **Backend API**: Developed with FastAPI exposing CRUD endpoints over the database schema with auto-generated OpenAPI docs.
* **Auth & Authorization**: JWT token sessions; role-based access control (Librarian vs Member) enforced on write endpoints.
* **Background Jobs**: Asynchronous overdue borrow scan checks managed by a scheduled Celery daemon using Redis as a message broker.
* **Frontend UI**: Responsive, single-screen light mode React UI for user login, dynamic subject dropdown filters, compact scrollable modals, interactive counter switchers, and real-time SSE notifications.

---

## Setup & Local Running Guide

### Method 1: Running with Docker Compose (Recommended)
You can launch the entire ecosystem (FastAPI, React UI, PostgreSQL, Redis, Celery Worker) using a single command:

1. Start the services directly from the project root:
   ```bash
   docker compose up --build -d
   ```
   This boots:
   * **Frontend Client**: `http://localhost:3000` (React Web UI)
   * **FastAPI Backend**: `http://localhost:8000` (API Docs at `http://localhost:8000/docs`)
   * **PostgreSQL Database**: `localhost:5432`
   * **Redis Queue Broker**: `localhost:6379`
   * **Celery Worker**: Background daemon listening to Redis queues.

---

### Method 2: Running Components Locally

Ensure PostgreSQL is running locally on port `5432` and Redis is running on port `6379`.

#### Step 1: Database Migrations & Seeding
Note: The `database/` folder is a shared resource directory. To execute database routines locally, run commands from inside the `database/` directory using the virtual environment paths from the `cli/` folder:

1. Build the virtual environment inside the `cli/` folder:
   ```bash
   cd cli
   uv sync
   ```
2. Navigate to the `database/` folder:
   ```bash
   cd ../database
   ```
3. Run database migrations:
   * **Windows PowerShell**:
     ```powershell
     ..\cli\.venv\Scripts\alembic upgrade head
     ```
   * **macOS/Linux**:
     ```bash
     ../cli/.venv/bin/alembic upgrade head
     ```
4. Populate database with seed data (mock members, librarians, 17 catalog books):
   * **Windows PowerShell**:
     ```powershell
     ..\cli\.venv\Scripts\python seed_data\seed.py
     ```
   * **macOS/Linux**:
     ```bash
     ../cli/.venv/bin/python seed_data/seed.py
     ```

#### Step 2: Running the Web API Backend
1. Navigate to the `backend/` folder and sync dependencies:
   ```bash
   cd ../backend
   uv sync
   ```
2. Create your environment configuration in `backend/.env`:
   ```env
   DATABASE_URL=postgresql://lms_user:lms_password@localhost:5432/lms_db
   JWT_SECRET=supersecretjwtkeythatisextremelysecure123!
   REDIS_URL=redis://localhost:6379/0
   ```
3. Launch the FastAPI server:
   ```bash
   uv run uvicorn app.api.main:app --reload --port 8000
   ```

#### Step 3: Running the Celery Worker
In another terminal inside the `backend/` folder, launch the background daemon:
```bash
uv run celery -A workers.celery_app worker --loglevel=info
```

#### Step 4: Running the React Frontend
1. Navigate to the `frontend/` folder and install dependencies:
   ```bash
   cd ../frontend
   npm install
   ```
2. Launch the development server:
   ```bash
   npm run dev
   ```
3. Access the web interface at `http://localhost:3000`.

#### Step 5: Running the CLI Client
1. Navigate to the `cli/` folder:
   ```bash
   cd ../cli
   ```
2. Execute CLI operations:
   ```bash
   # List active books in database
   uv run python -m src.main book list
   
   # Add a book
   uv run python -m src.main book add --title "Clean Architecture" --author "Robert C. Martin" --isbn "9780134494166" --copies 4 --genre "Software Architecture"
   
   # Register a new library member
   uv run python -m src.main member register --first-name "Fizza" --last-name "Ali" --email "fizza@gmail.com" --phone "555-0101"
   
   # Borrow a book
   uv run python -m src.main loan borrow --member-email "fizza@gmail.com" --isbn "9780134494166"
   
   # Check active / overdue checkouts
   uv run python -m src.main loan active
   ```

---

## AWS EC2 Production Server Setup

To deploy the stack on your AWS EC2 instance:

### Step A: Set up Docker
SSH into your EC2 instance (Ubuntu 22.04 LTS) and run:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
```
*(Log out and log back in to apply group permissions).*

### Step B: Authenticate with GHCR
On your EC2 instance, log in to the GitHub Container Registry:
```bash
docker login ghcr.io -u YOUR_GITHUB_USERNAME
```

### Step C: Configure Variables & Start Stack
Create a directory for the app, copy the `docker-compose.prod.yml` file, configure your `.env` variables, and start the system:
```bash
mkdir lms && cd lms
cat <<EOT > .env
GH_REPO=your_github_username/library-management-system
JWT_SECRET_KEY=generate_a_random_secure_secret_key_here
SECRET_KEY=generate_a_random_secure_secret_key_here
EOT

docker-compose -f docker-compose.prod.yml up -d
```
Your FastAPI Swagger docs are accessible at `http://YOUR_EC2_IP:8000/docs`, and the React frontend client is live at `http://YOUR_EC2_IP:80`.
