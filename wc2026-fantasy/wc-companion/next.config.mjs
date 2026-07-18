/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    serverComponentsExternalPackages: ["@prisma/client"],
    // getSnapshot() reads data/snapshot.json via fs at runtime. On serverless
    // hosts (Vercel) the file must be traced into each function bundle or the
    // read 404s — force it in for every route.
    outputFileTracingIncludes: {
      "/**": ["./data/snapshot.json"],
    },
  },
};

export default nextConfig;
