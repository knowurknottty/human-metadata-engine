export default async (request) => {
  const origin = Netlify.env.get("HME_API_ORIGIN");

  if (!origin) {
    return Response.json(
      {
        error: "The analysis API is not configured.",
        detail: "Set the Netlify environment variable HME_API_ORIGIN to the HTTPS origin running webapp/server.py.",
      },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }

  const incoming = new URL(request.url);
  const target = new URL(incoming.pathname + incoming.search, origin.replace(/\/$/, "") + "/");
  const headers = new Headers(request.headers);
  headers.delete("host");
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
    responseHeaders.set("Access-Control-Allow-Origin", incoming.origin);
    responseHeaders.set("Vary", "Origin");

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
      { status: 502, headers: { "Cache-Control": "no-store" } },
    );
  }
};

export const config = { path: "/api/*" };
