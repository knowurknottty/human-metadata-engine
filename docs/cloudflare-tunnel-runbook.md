# Secure public ingress with Cloudflare Tunnel

The current GCP VM must not remain publicly reachable over HTTP once a custom
hostname is configured. Cloudflare Tunnel supplies browser HTTPS while keeping
the Python origin private.

## Required external setup

1. Add the intended domain to Cloudflare DNS.
2. In **Zero Trust → Networks → Tunnels**, create a token-based tunnel and add
   one public hostname for the application.
3. Store the copied token only in the VM's secret environment; never commit it.

## VM cutover

After the tunnel reports healthy, bind the app to loopback only and run the
tunnel connector on the same VM. The connector should route the public
hostname to `http://127.0.0.1:8084` and include a final 404 catch-all rule.

```bash
# App: no public host-port binding after this cutover.
docker rm -f human-metadata-engine
docker run -d --name human-metadata-engine --restart unless-stopped \
  -p 127.0.0.1:8084:8080 human-metadata-engine:<reviewed-image-tag>

# Run cloudflared with its token supplied from a protected environment file.
cloudflared tunnel --no-autoupdate run --token "$TUNNEL_TOKEN"
```

Then verify the HTTPS hostname with `/api/health`, remove the GCP ingress rule
for TCP/8084, and confirm that direct-IP HTTP no longer responds. Do not enable
HSTS until the hostname is serving a valid public certificate.

## Operational checks

```bash
cloudflared tunnel ingress validate
cloudflared tunnel ingress rule https://your-hostname.example
```

Keep the existing stopped Docker rollback container until the hostname, HTTPS,
analysis endpoint, and rate-limit behavior have passed validation.
