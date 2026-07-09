const allowedOrigin = (request) => {
  const origin = request.headers.get("origin");
  if (!origin) return "*";
  try {
    const host = new URL(origin).hostname;
    if (host === "knowurknottty.github.io" || host.endsWith(".netlify.app")) return origin;
  } catch (_) {}
  return "null";
};

const corsHeaders = (request) => ({
  "Access-Control-Allow-Origin": allowedOrigin(request),
  "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Max-Age": "86400",
  "Vary": "Origin",
});

export default async (request) => {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(request) });
  }

  const origin = Netlify.env.get("HME_API_ORIGIN");
  if (!origin) {
    return Response.json(
      {
        error: "The analysis API is not configured.",
        detail: "Set HME_API_ORIGIN to the HTTPS origin running webapp/server.py.",
      },
      { status: 503, headers: { "Cache-Control": "no-store", ...corsHeaders(request) } },
    );
  }

  const incoming = new URL(request.url);
  const target = new URL(incoming.pathname + incoming.search, origin.replace(/\/$/, "") + "/");
  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("origin");
  headers.set("x-forwarded-host", incoming.host);
  headers.set("x-forwarded-proto", incoming.protocol.replace(":", ""));

  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body: request.method === "GET" || request.method === "HEAD" ? undefined : request.body,
      redirect: "manual",
    });

    const responseHeaders = new Headers(upstream.headers);
    responseHeaders.set("Cache-Control", "no-store");
    for (const [key, value] of Object.entries(corsHeaders(request))) {
      responseHeaders.set(key, value);
    }

    return new Response(upstream.body, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    return Response.json(
      {
        error: "The analysis service is unavailable.",
        detail: error instanceof Error ? error.message : String(error),
      },
      { status: 502, headers: { "Cache-Control": "no-store", ...corsHeaders(request) } },
    );
  }
};

export const config = { path: "/api/*" };
