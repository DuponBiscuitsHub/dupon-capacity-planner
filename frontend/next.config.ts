import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Genera un bundle mínimo auto-contenido (node server.js).
  // Reduce la imagen Docker de ~500 MB a ~50 MB.
  output: "standalone",
};

export default nextConfig;
