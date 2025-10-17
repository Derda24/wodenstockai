/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
  env: {
    NEXT_PUBLIC_APP_NAME: 'WODEN Stock AI',
    NEXT_PUBLIC_APP_VERSION: '2.0.0',
  },
  images: {
    domains: ['localhost'],
  },
}

module.exports = nextConfig
