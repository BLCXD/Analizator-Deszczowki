FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY static ./static
RUN addgroup --system web && adduser --system --ingroup web web \
    && mkdir -p /data && chown -R web:web /app /data
USER web

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "100", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
