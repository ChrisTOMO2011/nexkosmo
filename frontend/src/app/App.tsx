import { CharacterIdentityPage } from "../pages/CharacterIdentityPage";

const characterIdentityRoute =
  /^\/studio\/projects\/[^/]+\/pre-production\/characters\/[^/]+\/?$/;

export function AppRoutes() {
  if (!characterIdentityRoute.test(window.location.pathname)) {
    return (
      <main className="route-fallback">
        <h1>Studio page not found</h1>
        <a href="/studio/projects/the-last-dawn/pre-production/characters/christopher">
          Open Character Identity
        </a>
      </main>
    );
  }

  return <CharacterIdentityPage />;
}
