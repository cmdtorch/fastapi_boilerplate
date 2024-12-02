# 🌟 FastAPI Project Starter

Welcome to the 🚀 **FastAPI Project Starter**! This guide will help you set up and run your FastAPI project quickly and efficiently. It covers essential topics like 🔧 installation, 📦 dependencies, and 🖥️ running the development server.

## ✨ Features
- 📂 Repository management
- 🔐 Authentication
- 🛡️ Middlewares (session)
- ⚠️ Exception handling
- 🛠️ SQLAlchemy
- 🧪 Pytest

## ⚙️ Installation

### 🔽 Install `uv` (Optional)
The `uv` tool simplifies 📋 dependency management and running the development server. Follow the steps below to install it based on your 🖥️ operating system:

#### 🪟 For Windows
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 🐧 For Linux and 🍎 macOS
Using `curl`:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Using `wget`:
```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

**ℹ️ Note**: For more details or troubleshooting, visit the [official UV installation documentation](https://docs.astral.sh/uv/getting-started/installation/).

---

### 📦 Install Dependencies

#### Using `uv`:
```bash
uv sync
```

#### Using `pip`:
```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Server

#### Using `uv`:
```bash
uv run fastapi dev
```

#### Using `fastapi-cli`:
```bash
fastapi dev
```

#### Using `uvicorn` directly:
```bash
uvicorn app.main:app
```

Once the server is running, your application will be served at:
- 🌐 **Base URL**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📄 **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

