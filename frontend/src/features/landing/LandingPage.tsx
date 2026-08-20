const studioEntryRoute = "/studio";

export function LandingPage() {
  return (
    <main className="landing-page">
      <h1>Nexkosmo</h1>
      <p>The cinematic landing is served directly at this route.</p>
      <a className="landing-page__skip" href={studioEntryRoute}>
        Open Nexkosmo Studio
      </a>
    </main>
  );
}
