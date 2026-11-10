FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home --uid 10001 portal
COPY --chown=portal:portal . .
RUN mkdir -p /app/staticfiles && chown -R portal:portal /app
USER portal
CMD ["sh", "start.sh"]
