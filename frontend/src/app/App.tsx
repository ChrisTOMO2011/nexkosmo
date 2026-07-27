import { CharacterIdentityPage } from "../features/studio/pre-production";
import { RenderPage } from "../features/studio/render";
import { ReviewPage } from "../features/studio/review";
import { SetPage } from "../features/studio/set";
import { StudioPage } from "../features/studio/studio";
import { LandingPage } from "../features/landing/LandingPage";
import { resolveStudioRoute } from "./routes";

export function AppRoutes() {
  const route = resolveStudioRoute(window.location.pathname);

  if (route.kind === "home") {
    return <LandingPage />;
  }

  if (route.kind === "character") {
    return (
      <CharacterIdentityPage
        projectId={route.projectId}
        characterId={route.characterId}
      />
    );
  }

  if (route.kind === "workflow") {
    const props = { projectId: route.projectId };
    if (route.stage === "set") return <SetPage {...props} />;
    if (route.stage === "studio") return <StudioPage {...props} />;
    if (route.stage === "review") return <ReviewPage {...props} />;
    return <RenderPage {...props} />;
  }

  return (
    <main className="route-fallback">
      <h1>Studio page not found</h1>
      <a href="/">Return to Nexkosmo home</a>
      <a href="/studio/projects/the-last-dawn/pre-production/characters/christopher">
        Open Character Identity
      </a>
    </main>
  );
}
