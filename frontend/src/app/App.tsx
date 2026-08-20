import { useCallback, useEffect, useState, type ReactNode } from "react";
import { flushSync } from "react-dom";
import { CharacterIdentityPage } from "../features/studio/pre-production";
import { EnvironmentPage } from "../features/studio/pre-production/environment";
import { RenderPage } from "../features/studio/render";
import { SetPage } from "../features/studio/set";
import { StudioPage } from "../features/studio/studio";
import { LandingPage } from "../features/landing/LandingPage";
import { DiscoveryPage } from "../features/discovery";
import { MomentWorkspacePage } from "../features/discovery/MomentWorkspacePage";
import { IdeaPage } from "../features/studio/idea";
import { ReadyPage } from "../features/studio/ready";
import { ShapePage } from "../features/studio/shape";
import {
  readStudioEntryContext,
  rememberStudioEntryContext,
  resolveStudioRoute,
} from "./routes";
import {
  APP_NAVIGATION_EVENT,
  type AppNavigationDetail,
} from "./navigation";

type ViewTransitionDocument = Document & {
  startViewTransition?: (update: () => void) => { finished: Promise<void> };
};

function prefersReducedMotion() {
  return (
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

export function AppRoutes() {
  const [locationKey, setLocationKey] = useState(
    () => `${window.location.pathname}${window.location.search}`,
  );

  const navigate = useCallback((href: string, replace = false) => {
    const destination = new URL(href, window.location.href);
    if (destination.origin !== window.location.origin) {
      window.location.assign(destination.href);
      return;
    }

    const nextLocation = `${destination.pathname}${destination.search}`;
    if (nextLocation === `${window.location.pathname}${window.location.search}`) {
      return;
    }

    const update = () => {
      if (replace) {
        window.history.replaceState({}, "", destination.href);
      } else {
        window.history.pushState({}, "", destination.href);
      }
      flushSync(() => setLocationKey(nextLocation));
      if (!window.navigator.userAgent.includes("jsdom")) {
        window.scrollTo({ top: 0, behavior: "instant" });
      }
    };

    const documentWithTransitions = document as ViewTransitionDocument;
    if (
      documentWithTransitions.startViewTransition &&
      !prefersReducedMotion()
    ) {
      documentWithTransitions.startViewTransition(update);
    } else {
      update();
    }
  }, []);

  useEffect(() => {
    const handlePopState = () => {
      const nextLocation = `${window.location.pathname}${window.location.search}`;
      const update = () => flushSync(() => setLocationKey(nextLocation));
      const documentWithTransitions = document as ViewTransitionDocument;
      if (
        documentWithTransitions.startViewTransition &&
        !prefersReducedMotion()
      ) {
        documentWithTransitions.startViewTransition(update);
      } else {
        update();
      }
    };

    const handleNavigation = (event: Event) => {
      const detail = (event as CustomEvent<AppNavigationDetail>).detail;
      navigate(detail.href, detail.replace);
    };

    const handleLinkClick = (event: MouseEvent) => {
      if (
        event.defaultPrevented ||
        event.button !== 0 ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey ||
        event.altKey
      ) {
        return;
      }
      const target = event.target as Element | null;
      const anchor = target?.closest<HTMLAnchorElement>("a[href]");
      if (!anchor || anchor.target || anchor.download) return;
      const destination = new URL(anchor.href, window.location.href);
      if (destination.origin !== window.location.origin) return;
      event.preventDefault();
      navigate(destination.href);
    };

    window.addEventListener("popstate", handlePopState);
    window.addEventListener(APP_NAVIGATION_EVENT, handleNavigation);
    document.addEventListener("click", handleLinkClick);
    return () => {
      window.removeEventListener("popstate", handlePopState);
      window.removeEventListener(APP_NAVIGATION_EVENT, handleNavigation);
      document.removeEventListener("click", handleLinkClick);
    };
  }, [navigate]);

  const remembered = readStudioEntryContext(window.localStorage);
  const route = resolveStudioRoute(
    window.location.pathname,
    window.location.search,
    remembered,
  );

  let page: ReactNode;

  if (route.kind === "home") {
    page = <LandingPage />;
  } else if (route.kind === "discovery") {
    page = <DiscoveryPage />;
  } else if (route.kind === "discovery-moment") {
    page = <MomentWorkspacePage momentId={route.momentId} />;
  } else if (route.kind === "invalid-context") {
    page = (
      <main className="route-fallback" role="alert">
        <h1>Studio context unavailable</h1>
        <p>{route.detail}</p>
        <a href="/">Return to Nexkosmo home</a>
      </main>
    );
  } else if (route.kind === "character") {
    rememberStudioEntryContext(window.localStorage, {
      projectId: route.projectId,
      characterId: route.characterId,
    });
    page = (
      <CharacterIdentityPage
        projectId={route.projectId}
        characterId={route.characterId}
      />
    );
  } else if (route.kind === "environment") {
    page = (
      <EnvironmentPage
        projectId={route.projectId}
        environmentId={route.environmentId}
      />
    );
  } else if (route.kind === "workflow") {
    const props = { projectId: route.projectId };
    if (route.stage === "idea") page = <IdeaPage {...props} />;
    else if (route.stage === "shape") page = <ShapePage {...props} />;
    else if (route.stage === "ready") page = <ReadyPage {...props} />;
    else if (route.workspace === "set") page = <SetPage {...props} />;
    else if (route.workspace === "render") page = <RenderPage {...props} />;
    else page = <StudioPage {...props} />;
  } else {
    page = (
      <main className="route-fallback">
        <h1>Studio page not found</h1>
        <a href="/">Return to Nexkosmo home</a>
        <a href="/studio">Open Nexkosmo Studio</a>
      </main>
    );
  }

  return (
    <div
      className="app-route-transition"
      data-location={locationKey}
      key={locationKey}
    >
      {page}
    </div>
  );
}
