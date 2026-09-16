const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

const HOP_BY_HOP_HEADERS = new Set([
  'connection',
  'keep-alive',
  'proxy-authenticate',
  'proxy-authorization',
  'te',
  'trailer',
  'transfer-encoding',
  'upgrade',
  'content-length',
]);

function backendUrl(path: string) {
  return new URL(path, BACKEND_BASE_URL);
}

function copyRequestHeaders(headers: Headers) {
  const forwarded = new Headers(headers);
  forwarded.delete('host');
  forwarded.delete('origin');
  forwarded.delete('referer');
  forwarded.delete('content-length');
  return forwarded;
}

function copyResponseHeaders(headers: Headers) {
  const forwarded = new Headers();
  headers.forEach((value, key) => {
    if (!HOP_BY_HOP_HEADERS.has(key.toLowerCase())) {
      forwarded.set(key, value);
    }
  });
  return forwarded;
}

export async function proxyRequest(request: Request, backendPath: string) {
  const method = request.method.toUpperCase();
  const init: RequestInit = {
    method,
    headers: copyRequestHeaders(request.headers),
    cache: 'no-store',
  };

  if (method !== 'GET' && method !== 'HEAD') {
    const buf = await request.arrayBuffer();
    if (buf && buf.byteLength && buf.byteLength > 0) {
      init.body = buf;
    }
  }

  const response = await fetch(backendUrl(backendPath), init);

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: copyResponseHeaders(response.headers),
  });
}
