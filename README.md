
---

# 🎬 Movie Recommendation API

A **FastAPI**-based backend service that recommends movies using vector similarity and manages movie metadata stored in a **PostgreSQL** or **SQLite** database.

## 🚀 Features

* ✅ Recommend movies based on liked movie IDs (content-based filtering)
* ✅ Manage users and track liked movies
* ✅ Secure endpoints with JWT-based authentication
* ✅ Store & retrieve movie metadata with vector embeddings
* ✅ Pytest test suite with results in HTML
* ✅ Swagger UI (`/docs`) for quick testing

## 🧪 Preview

> Below is a preview of the working `/docs` interface

![Swagger UI Screenshot](Capture.png)

## 📦 Tech Stack

* FastAPI
* SQLAlchemy (Async)
* PostgreSQL / SQLite
* NumPy, Pandas
* Sentence Transformers

## 🧰 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/wlvUmar/RecAPI.git
cd RecAPI
```

### 2. Create and activate virtualenv (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API

```bash
uvicorn app.main:app --reload
```

