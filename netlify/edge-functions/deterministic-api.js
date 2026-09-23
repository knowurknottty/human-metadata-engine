const ROUTES = Object.freeze({
  "/api/health": new Set(["GET", "HEAD"]),
  "/api/version": new Set(["GET", "HEAD"]),
  "/api/analyze": new Set(["POST"]),
  "/api/report-download": new Set(["GET", "POST"]),
  "/api/tarot": new Set(["POST"]),
  "/api/tarot/spreads": new Set(["GET", "HEAD"]),
});

const json = (payload, status, extraHeaders = {}) =>
  Response.json(payload, {
    status,
    headers: {
      "Cache-Control": "no-store",
      ...extraHeaders,
    },
  });

export default async (request) => {
  const incoming = new URL(request.url);
  const allowedMethods = ROUTES[incoming.pathname];

  if (!allowedMethods) {
    return json({ error: "Not found." }, 404);
  }

  if (!allowedMethods.has(request.method)) {
    return json(
      { error: "Method not allowed." },
      405,
      { Allow: [...allowedMethods].join(", ") },
    );
  }

  const configuredOrigin = Netlify.env.get("HME_API_ORIGIN");
  if (!configuredOrigin) {
    return json(
      {
        error: "The deterministic analysis service is not configured.",
        detail: "HME_API_ORIGIN must point to the HTTPS Human Manual engine.",
      },
      503,
    );
  }

  let origin;
  try {
    origin = new URL(configuredOrigin);
  } catch {
    return json({ error: "The deterministic analysis service is misconfigured." }, 503);
  }

  if (origin.protocol !== "https:") {
    return json({ error: "The deterministic analysis service requires HTTPS." }, 503);
  }

  const target = new URL(incoming.pathname + incoming.search, origin);
  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("origin");
  headers.set("x-forwarded-host", incoming.host);
  headers.set("x-forwarded-proto", "https");

  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body: request.method === "GET" || request.method === "HEAD" ? undefined : request.body,
      redirect: "manual",
    });

    const responseHeaders = new Headers(upstream.headers);
    responseHeaders.set("Cache-Control", "no-store");

    return new Response(upstream.body, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers: responseHeaders,
    });
  } catch {
    return json({ error: "The deterministic analysis service is unavailable." }, 502);
  }
};

export const config = {
  path: [
    "/api/health",
    "/api/version",
    "/api/analyze",
    "/api/report-download",
    "/api/tarot",
    "/api/tarot/spreads",
  ],
};
