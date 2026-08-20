import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv, type Plugin } from "vite";

function cinematicLandingAtRoot(): Plugin {
  const installRewrite = (server: {
    middlewares: {
      use: (
        handler: (
          request: { url?: string },
          response: unknown,
          next: () => void,
        ) => void,
      ) => void;
    };
  }) => {
    server.middlewares.use((request, _response, next) => {
      const [pathname, query] = (request.url ?? "/").split("?", 2);
      if (pathname === "/") {
        request.url = `/landing/index.html${query ? `?${query}` : ""}`;
      } else if (
        pathname === "/discovery" ||
        pathname === "/discovery/" ||
        pathname === "/studio" ||
        pathname.startsWith("/studio/")
      ) {
        request.url = `/index.html${query ? `?${query}` : ""}`;
      }
      next();
    });
  };

  return {
    name: "nexkosmo-cinematic-landing-at-root",
    configureServer: installRewrite,
    configurePreviewServer: installRewrite,
  };
}

export default defineConfig(({ mode }) => {
  const environment = loadEnv(mode, ".", "");

  return {
    plugins: [cinematicLandingAtRoot(), react()],
    server: {
      host: "127.0.0.1",
      port: 4173,
      proxy: {
        "/api": environment.VITE_NEXKOSMO_DEV_PROXY_TARGET ?? "http://127.0.0.1:8000",
      },
    },
    preview: {
      host: "127.0.0.1",
      port: 4173,
    },
  };
});
