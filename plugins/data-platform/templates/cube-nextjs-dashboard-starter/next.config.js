/** @type {import('next').NextConfig} */
// CSP added after mandatory security review: connect-src is the load-bearing
// directive for this no-iframe (direct-API) embed pattern — see
// ../../skills/embed-csp-and-iframe-sandboxing/SKILL.md "Cube (with custom
// React UI)". Set CUBE_API_ORIGIN to the ORIGIN ONLY (scheme+host[:port]) of
// your Cube instance, e.g. "https://cube.client-domain.com" — do not include
// a path.
const CUBE_API_ORIGIN = process.env.CUBE_API_ORIGIN || "http://localhost:4000";

const nextConfig = {
  reactStrictMode: true,
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              `connect-src 'self' ${CUBE_API_ORIGIN}`,
              "frame-ancestors 'self'",
              "img-src 'self' data:",
              "object-src 'none'",
              "base-uri 'self'",
            ].join("; "),
          },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
