# Purpose: Describe the learning API container
# Learn: Inspect dependency installation, non-root execution and the Gunicorn server.
# Run: Optional container route only: follow azure_execution/app_service/README.md. Requires Docker outside Databricks; build creates an image and running it starts a persistent server.

FROM python:3.11-slim
WORKDIR /app
COPY requirements ./requirements
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY data ./data
RUN useradd --create-home appuser
USER appuser
ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "academy.api:application"]
