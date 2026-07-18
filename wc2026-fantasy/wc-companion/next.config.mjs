/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // The engine snapshot lives outside the app dir; allow reading it at runtime.
  experimental: { serverComponentsExternalPackages: ["@prisma/client"] },
};

export default nextConfig;
