import { proxyRequest } from '../../_proxy';

function backendPath(pathSegments: string[] | undefined) {
  if (!pathSegments || pathSegments.length === 0) {
    return '/essays/';
  }

  return `/essays/${pathSegments.join('/')}`;
}

async function handler(
  request: Request,
  context: { params: Promise<{ path?: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, backendPath(params.path));
}

export async function GET(request: Request, context: any) {
    return handler(request, context);
  }
  
  export async function POST(request: Request, context: any) {
    return handler(request, context);
  }
  
  export async function PUT(request: Request, context: any) {
    return handler(request, context);
  }
  
  export async function DELETE(request: Request, context: any) {
    return handler(request, context);
  }