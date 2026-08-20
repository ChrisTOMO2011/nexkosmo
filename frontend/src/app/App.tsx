import { StagePlaceholder } from "../components/shell/StagePlaceholder";
import { SafeRouteState } from "../components/shell/SafeRouteState";
import { StudioLayout } from "../layouts/StudioLayout";
import { resolveAppRoute } from "./routes";

export function App() {
  const route = resolveAppRoute(window.location.pathname);

  if (route.kind !== "stage") {
    return <SafeRouteState kind={route.kind} />;
  }

  return (
    <StudioLayout activeStage={route.stage} projectId={route.projectId}>
      <StagePlaceholder stage={route.stage} />
    </StudioLayout>
  );
}

