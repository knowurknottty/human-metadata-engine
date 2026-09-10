# Human Metadata Atlas launch evidence — 2026-09-10 UTC

## Available demos

- Netlify: https://inversionlabs-hmd.netlify.app (public).
- Sites: https://human-metadata-atlas.knowurknottty.chatgpt.site (owner-private).
- GitHub branch: `codex/richer-deterministic-readings`.

The richer authored narrative and all three tarot spreads are deployed. No AI
provider, model, API key, paid plan, or billing enablement was configured.

## Exact deployment chain

| Surface | Source / package | Returned deployment |
| --- | --- | --- |
| Python backend | `39e3404b997b5d5c5e3c0531cfdb84325faa30fc`; Docker `human-metadata-engine:39e3404b997b` | Live `/api/health` returns this exact revision, version 1.0.0, ephemeris available, 129 references, no reference errors |
| Netlify | Shared `webapp/static` and edge proxy from `39e3404b997b5d5c5e3c0531cfdb84325faa30fc` | `6aa22f7798a26e5bc4ab7f0d`, returned `ready`; published 2026-09-10T04:18:00Z |
| Sites version 2 | Pushed `f9d6340c2e2c11db04e3aeeaae3639c3edcce5bc`; archive SHA256 `0c3b77e6c1671793b628084813d1f8377ea3631a2411463f13995a66f594bff3` | `appgdep_6aa2303574208191889ab6de47ccd1ee`, returned `succeeded`, environment revision 1 |

Sites project ID is recorded in `.openai/hosting.json`. Its second version fixes
forwarding of the report-download redirect; the Python and frontend product
source are unchanged from the first deployment. Sites serves the same authored
HTML/CSS/JavaScript, bundled by `scripts/build_sites.mjs`, with an HTTPS API proxy.

## Verification

- `.venv/bin/python -m pytest -q`: 318 passed, 95 subtests passed.
- `.venv/bin/python tools/run_tests.py --quiet`: 44 files, 0 failures.
- `.venv/bin/python tools/validate_contracts.py`: `PUBLIC_CONTRACTS_VALID`.
- JavaScript syntax checks and `git diff --check` passed.
- Live HTTPS checks through both Netlify and authenticated Sites returned
  health and all three spreads: focus (1), situation (3), crossroads (5).
- A generic exact-birth fixture returned 17 narrative chapters on each host,
  with all three narrative-mode verifiers valid.
- Both hosts completed the form-POST/redirect/GET download flow, returning the
  full 72,009-byte report exactly as generated.
- Netlify JavaScript and CSS bytes were compared with the local committed files.
- Direct public HTTP to the old VM port 8084 now refuses connections. Docker
  reports the app bound to `127.0.0.1:8084`, with `unless-stopped` supervision.
- Local browser interaction evidence covers the three spread choices, chapter
  navigation and mode switching. This is not physical iPhone/Android evidence.

## Remaining launch limitation — permanent HTTPS backend

**These are demos, not a completed dependable production release.** The current
API origin is `https://buyer-thumbs-lawn-nine.trycloudflare.com`, a temporary
Cloudflare Quick Tunnel. It has no uptime guarantee and its hostname can change
if the tunnel is recreated. Both hosts use `HME_API_ORIGIN`; a replacement needs
to be configured and deployed on both hosts.

The existing GCP VM is `biocapt-ecosystem`, project `biocapt`, zone
`europe-west1-b`. The application and `hme-demo-tunnel` containers have restart
policies. The tunnel image is pinned to
`cloudflare/cloudflared@sha256:ff69a2225ad7c6f85ed84fbd5f3087df46202426b2388ec60214098e0adf05e9`.
The rollback app container is `human-metadata-engine-rollback-39e3404b997b`.

Two permanent-hosting attempts were rejected by GCP with `BILLING_DISABLED`:
`gcloud run deploy human-metadata-engine ... --source=...` and
`gcloud compute firewall-rules create allow-https-hme ...`. Billing was left
disabled, and no paid upgrade was made. A Cloudflare named tunnel with an
existing domain, or another permanent HTTPS API origin, can remove this blocker.
The Cloudflare runbook explains the intended permanent tunnel setup.

Physical-device QA and the remaining broader release gates have not been marked
complete. Unrelated Android work and local untracked files were preserved.

## Updating either host

1. Validate and push a coherent source revision. Deploy backend changes with
   `scripts/deploy_gcp.sh` using that full revision.
2. Netlify is linked to `inversionlabs-hmd`. Publish `webapp/static` together
   with `netlify/edge-functions/api-proxy.js` and `netlify.toml`.
3. Build Sites using `node scripts/build_sites.mjs`; push to the existing Sites
   source repository with a fresh ephemeral credential, package the exact
   source's output, save and deploy a new version for the existing project.
4. Check returned terminal deployment status, health revision, each spread,
   full analysis, and report export through both origins.

Do not use the temporary tunnel as evidence that the stable-ingress gate passed.
