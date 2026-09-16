import { proxyRequest } from '../../_proxy';

function backendPath(pathSegments: string[] | undefined) {
  if (!pathSegments || pathSegments.length === 0) {
    return '/questions/';
  }

  return `/questions/${pathSegments.join('/')}`;
}

async function handler(request: Request, context: { params: Promise<{ path?: string[] }> }) {
  const params = await context.params;
  return proxyRequest(request, backendPath(params.path));
}

export async function GET(request: Request, context: { params: Promise<{ path?: string[] }> }) {
  return handler(request, context);
}
