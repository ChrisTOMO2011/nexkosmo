const studioEntryRoute =
  "/studio/projects/the-last-dawn/pre-production/characters/christopher";

export function LandingPage() {
  return (
    <main className="landing-page">
      <iframe
        className="landing-page__frame"
        src="/landing/index.html"
        title="Nexkosmo cinematic home"
      />
      <a className="landing-page__skip" href={studioEntryRoute}>
        Open Nexkosmo Studio
      </a>
    </main>
  );
}
