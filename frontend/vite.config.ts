import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// De dev-server draait op poort 5173; de API op 8000 (zie CORS_ORIGINS in backend/.env.example).
export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
});
