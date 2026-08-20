import { useState } from "react";
import { beginLogin } from "../../auth/session";
import { CanonicalLogo } from "../brand/CanonicalLogo";
import { Button, Panel } from "../ui";

export function SignIn() {
  const [error, setError] = useState("");
  return (
    <div className="safe-route-state">
      <CanonicalLogo />
      <main>
        <Panel className="safe-route-state__panel">
          <h1>Sign in to Nexkosmo</h1>
          <p>Your deployment’s configured OIDC provider verifies your identity.</p>
          {error && <p role="alert">{error}</p>}
          <Button
            variant="outlined"
            onClick={() => void beginLogin().catch((reason: Error) => setError(reason.message))}
          >
            Continue securely
          </Button>
        </Panel>
      </main>
    </div>
  );
}
