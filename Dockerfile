ARG PYTHON_BASE=python:3.12-slim-bookworm@sha256:db8e83a44af476c636a6a753adace39ad37863b63c0afd2862db7bbafeeb3944
FROM ${PYTHON_BASE} AS ephemeris-builder

WORKDIR /build

COPY requirements.txt .

# pyswisseph ships Swiss Ephemeris C sources. Build it in an isolated stage so
# compilers never reach the runtime image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential pkg-config \
    && python3 -m pip wheel --require-hashes --no-cache-dir --wheel-dir /wheels -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

FROM ${PYTHON_BASE}

ARG HME_BUILD_REVISION=unknown
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    HME_BIND_HOST=0.0.0.0 \
    HME_BUILD_REVISION=${HME_BUILD_REVISION}

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
