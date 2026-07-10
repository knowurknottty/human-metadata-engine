FROM python:3.12-slim AS ephemeris-builder

WORKDIR /build

COPY requirements.txt .

# pyswisseph ships Swiss Ephemeris C sources. Build it in an isolated stage so
# compilers never reach the runtime image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential pkg-config \
    && python3 -m pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

COPY --from=ephemeris-builder /wheels /wheels
RUN python3 -m pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

COPY . /app

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["python3", "webapp/server.py"]
