# Deployment: Netlify/GitHub Pages + private Python origin

The application has two layers:

1. `webapp/static/` — the browser UI.
2. `webapp/server.py` — the Python analysis API and engine runtime.

GitHub Pages and Netlify static hosting do not run the long-lived Python server. This repository therefore uses a split deployment:

- **Netlify** serves the UI and provides a same-origin `/api/*` edge proxy.
- **GitHub Pages** serves a mirror of the UI and sends `/api/*` requests to the Netlify origin.
- **Python API host** runs `python3 webapp/server.py` on a service that supports persistent Python processes, such as Railway, Render, Fly.io, a VPS, or a container platform. The origin must be private or HTTPS-terminated; do not expose the GCP loopback service directly over HTTP.

## 1. Deploy the Python API

Run the repository with:

```bash
python3 webapp/server.py
```

The host must provide an HTTPS origin and pass its assigned port through `PORT`. On a VM, set `HME_BIND_HOST=127.0.0.1` and use the Cloudflare Tunnel runbook.

Verify:

```text
https://YOUR-PYTHON-HOST/healthz
https://YOUR-PYTHON-HOST/readyz
https://YOUR-PYTHON-HOST/api/version
```

Liveness should return `"status":"alive"`; readiness should contain
`"ready":true`. The legacy `/api/health` route remains a readiness alias.

## 2. Configure Netlify

Import this GitHub repository into Netlify. `netlify.toml` already configures:

- Publish directory: `webapp/static`
- Edge function route: `/api/*`
- SPA fallback
- Security headers

Create the Netlify environment variable:

```text
HME_API_ORIGIN=https://YOUR-PYTHON-HOST
```

Do not include a trailing slash.

Deploy, then verify:

```text
https://YOUR-SITE.netlify.app/api/health
```

This request should be proxied to the private HTTPS Python API. Restrict `HME_ALLOWED_ORIGINS` to the exact UI origin; do not use wildcard CORS.

## 3. Configure GitHub Pages

In repository settings:

1. Open **Settings → Pages**.
2. Set **Source** to **GitHub Actions**.
3. Open **Settings → Secrets and variables → Actions → Variables**.
4. Create the repository variable:

```text
HME_API_ORIGIN=https://YOUR-SITE.netlify.app
```

The `.github/workflows/pages.yml` workflow:

- Copies `webapp/static` into a Pages artifact.
- Converts root-relative asset paths for project Pages hosting.
- Injects a small API bridge that routes `/api/*` calls to Netlify.
- Deploys the result with the official GitHub Pages actions.

After merging to `main`, the workflow publishes:

```text
https://knowurknottty.github.io/human-metadata-engine/
```

## Request path

```text
GitHub Pages UI
  → Netlify /api/*
    → Netlify Edge proxy
      → Python API host
        → Human Metadata Engine
```

Netlify-hosted visitors use the same route beginning at Netlify, so the browser always calls `/api/*` without needing CORS-specific application code.

## Important

The Python API is required. Deploying only the static directory to either Netlify or GitHub Pages will render the interface but cannot execute the engine.
