import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// O build vai para dentro do Spring Boot, que serve as telas e a API no mesmo endereço.
export default defineConfig({
  plugins: [react()],
  build: { outDir: "../backend/src/main/resources/static", emptyOutDir: true },
  server: { proxy: { "/api": "http://localhost:8080" } },
});
