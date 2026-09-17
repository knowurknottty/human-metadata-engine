// `assets` is injected by build_sites.mjs from the shared frontend source.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const security = {
      'X-Content-Type-Options':'nosniff',
      'Referrer-Policy':'no-referrer',
      'Permissions-Policy':'camera=(), microphone=(), geolocation=()',
      'Content-Security-Policy':"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self'",
    };
    if (url.pathname.startsWith('/api/')) {
      if (!['GET', 'HEAD', 'POST'].includes(request.method)) return new Response('Method not allowed', {status:405, headers:security});
      let origin;
      try {
        origin = new URL(env.HME_API_ORIGIN);
        if (origin.protocol !== 'https:' || origin.username || origin.password || origin.origin === url.origin) throw new Error('Invalid origin');
      } catch {
        return Response.json({error:'The reading service is not configured.'}, {status:503, headers:{...security,'Cache-Control':'no-store'}});
      }
      const headers = new Headers();
      for (const name of ['content-type', 'accept']) if (request.headers.has(name)) headers.set(name, request.headers.get(name));
      try {
        const upstream = await fetch(new URL(url.pathname + url.search, origin.origin), {
          method:request.method, headers, redirect:'manual', duplex:'half',
          body:['GET','HEAD'].includes(request.method) ? undefined : request.body,
          signal:AbortSignal.timeout(35000),
        });
        const responseHeaders = new Headers(security);
        for (const name of ['content-type','content-disposition','retry-after','location']) if (upstream.headers.has(name)) responseHeaders.set(name, upstream.headers.get(name));
        responseHeaders.set('Cache-Control','no-store');
        return new Response(upstream.body, {status:upstream.status,headers:responseHeaders});
      } catch {
        return Response.json({error:'The reading service is temporarily unavailable. Please try again.'}, {status:502,headers:{...security,'Cache-Control':'no-store'}});
      }
    }
    if (!['GET','HEAD'].includes(request.method)) return new Response('Method not allowed', {status:405,headers:security});
    const asset = assets[url.pathname === '/' ? '/index.html' : url.pathname];
    if (!asset) return new Response('Not found', {status:404,headers:security});
    return new Response(request.method === 'HEAD' ? null : asset.body, {headers:{...security,'Content-Type':asset.type,'Cache-Control':'public, max-age=0, must-revalidate'}});
  },
};
