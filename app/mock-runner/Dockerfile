FROM python:3.12-slim

WORKDIR /opt/ad
COPY raspberry/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && addgroup --system mock && adduser --system --ingroup mock mock \
    && mkdir -p /data && chown -R mock:mock /data /opt/ad
COPY raspberry ./raspberry
COPY app/mock-runner/runner.py ./runner.py
USER mock
EXPOSE 8090
CMD ["python", "/opt/ad/runner.py"]
