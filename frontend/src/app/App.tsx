import { StagePlaceholder } from "../components/shell/StagePlaceholder";
import { SafeRouteState } from "../components/shell/SafeRouteState";
import { StudioLayout } from "../layouts/StudioLayout";
import { optionalSession } from "../auth/session";
import { AuthCallback } from "../components/auth/AuthCallback";
import { SignIn } from "../components/auth/SignIn";
import { CharacterWorkspace } from "../features/characters/CharacterWorkspace";
import { ProjectDirectory } from "../features/projects/ProjectDirectory";
import { resolveAppRoute } from "./routes";

export function App() {
  const route = resolveAppRoute(window.location.pathname);

  if (route.kind === "auth-callback") return <AuthCallback />;

  const session = optionalSession();
  if (!session) return <SignIn />;

  if (route.kind === "project-required") {
    return <ProjectDirectory session={session} />;
  }

  if (route.kind !== "stage") {
    return <SafeRouteState kind={route.kind} />;
  }

  return (
    <StudioLayout activeStage={route.stage} projectId={route.projectId}>
      {route.stage === "build" ? (
        <CharacterWorkspace session={session} projectId={route.projectId} />
      ) : (
        <StagePlaceholder stage={route.stage} />
      )}
    </StudioLayout>
  );
}
