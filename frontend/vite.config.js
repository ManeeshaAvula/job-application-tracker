import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// During development the Vite server proxies API calls to the FastAPI
// backend on port 8000, so the frontend can use relative URLs.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/applications": "http://127.0.0.1:8000",
      "/stats": "http://127.0.0.1:8000",
      "/health": "http://127.0.0.1:8000",
    },
  },
});
