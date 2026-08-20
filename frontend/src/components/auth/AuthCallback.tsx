import { useEffect, useState } from "react";
import { completeLogin } from "../../auth/session";
import { Panel } from "../ui";

export function AuthCallback() {
  const [error, setError] = useState("");
  useEffect(() => {
    void completeLogin(window.location.search)
      .then(() => window.location.replace("/studio"))
      .catch((reason: Error) => setError(reason.message));
  }, []);
  return (
    <main className="auth-callback">
      <Panel role="status">
        <h1>{error ? "Sign-in failed" : "Completing sign-in"}</h1>
        <p>{error || "Verifying the OIDC response…"}</p>
      </Panel>
    </main>
  );
}
