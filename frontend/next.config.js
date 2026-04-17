/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone", // pro Docker — menší image
  poweredByHeader: false,
  async rewrites() {
    // V dev módu necháme API requesty proxy na backend.
    // V produkci Caddy řeší routing.
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
  },
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000", "asistent.reality-pittner.cz"],
    },
  },
};

module.exports = nextConfig;
