import { proxyRequest } from '../_proxy';

export async function GET(request: Request) {
  return proxyRequest(request, '/user/');
}

export async function POST(request: Request) {
  return proxyRequest(request, '/user/');
}

export async function PUT(request: Request) {
  return proxyRequest(request, '/user/');
}

export async function DELETE(request: Request) {
  return proxyRequest(request, '/user/');
}
