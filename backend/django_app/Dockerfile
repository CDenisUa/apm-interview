FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Dev server is fine for an interview demo. For production you'd use
# gunicorn/uvicorn behind a proper ASGI/WSGI setup (see API.md / AZURE notes).
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
