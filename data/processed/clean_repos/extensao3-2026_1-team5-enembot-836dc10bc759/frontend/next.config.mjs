/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const api = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';
    return [
      {
        source: '/backend-api/:path*',
        destination: `${api}/:path*`,
      },
    ];
  },
  async redirects() {
    return [
      {
        source: '/chat/:subjectId',
        has: [{ type: 'query', key: 'build' }],
        destination: '/chat/:subjectId',
        permanent: false,
      },
    ];
  },
};

export default nextConfig;