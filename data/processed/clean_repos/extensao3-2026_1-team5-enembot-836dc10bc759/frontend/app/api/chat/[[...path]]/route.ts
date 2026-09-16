import { proxyRequest } from '../../_proxy';

function backendPath(pathSegments: string[] | undefined) {
  if (!pathSegments || pathSegments.length === 0) {
    return '/chat/';
  }

  if (pathSegments[0] === 'questions') {
    return `/questions/${pathSegments.slice(1).join('/')}`;
  }

  return `/chat/${pathSegments.join('/')}`;
}

async function handler(request: Request, context: { params: Promise<{ path?: string[] }> }) {
  const params = await context.params;
  return proxyRequest(request, backendPath(params.path));
}

export async function GET(request: Request, context: { params: Promise<{ path?: string[] }> }) {
  return handler(request, context);
}

export async function POST(request: Request, context: { params: Promise<{ path?: string[] }> }) {
  return handler(request, context);
}

export async function PUT(request: Request, context: { params: Promise<{ path?: string[] }> }) {
  return handler(request, context);
}

export async function DELETE(request: Request, context: { params: Promise<{ path?: string[] }> }) {
  return handler(request, context);
}
