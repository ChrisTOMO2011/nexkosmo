/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_OIDC_AUTHORIZATION_URL?: string;
  readonly VITE_OIDC_TOKEN_URL?: string;
  readonly VITE_OIDC_CLIENT_ID?: string;
  readonly VITE_OIDC_SCOPE?: string;
}

declare module "*.svg?url" {
  const source: string;
  export default source;
}
