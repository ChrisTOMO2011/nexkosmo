import { useState } from "react";
import {
  ArrowRight,
  ChevronDown,
  FileText,
  Heart,
  Image,
  Lightbulb,
  LockKeyhole,
  Mic2,
  Sparkles,
  Type,
} from "lucide-react";
import { navigateInApp } from "../../../app/navigation";
import sophiaPortrait from "../../../assets/idea/sophia-transparent.png";
import { TopNavigation } from "../../../components/studio/TopNavigation";

type IdeaMode = "type" | "speak" | "drop" | "import" | "surprise";

const ideaModes = [
  { id: "type", label: "Type", icon: Type },
  { id: "speak", label: "Speak", icon: Mic2 },
  { id: "drop", label: "Drop", icon: Image },
  { id: "import", label: "Import Script", icon: FileText },
  { id: "surprise", label: "Surprise Me", icon: Sparkles },
] as const;

export function IdeaPage({ projectId }: { projectId: string }) {
  const [idea, setIdea] = useState("");
  const [activeMode, setActiveMode] = useState<IdeaMode>("type");
  const [status, setStatus] = useState("");
  const hasIdea = idea.trim().length > 0;

  function selectMode(mode: IdeaMode, label: string) {
    setActiveMode(mode);
    if (mode === "type") {
      setStatus("Type your idea in the creative brief.");
      return;
    }
    if (mode === "speak") {
      setStatus("Voice capture will be connected when recording is available.");
      return;
    }
    if (mode === "drop") {
      setStatus("Image and file drop will be connected in a later phase.");
      return;
    }
    if (mode === "import") {
      setStatus("Script import will be connected in a later phase.");
      return;
    }
    setStatus(`${label} will be guided by Sophia when generation is available.`);
  }

  return (
    <main className="idea-page">
      <TopNavigation
        activeStage="idea"
        projectId={projectId}
        characterId="christopher"
        onPlaceholder={setStatus}
        ariaLabel="Creator workflow"
      />

      <div className="idea-page__stars" aria-hidden="true" />

      <aside className="idea-sophia" aria-label="Sophia, your AI Producer">
        <img
          className="idea-sophia__portrait"
          src={sophiaPortrait}
          alt="Sophia, AI Producer"
        />
        <section className="idea-sophia__card">
          <p className="idea-sophia__online"><span /> Online</p>
          <h2>SOPHIA</h2>
          <p className="idea-sophia__role">AI Producer</p>
          <div className="idea-sophia__rule" />
          <p className="idea-sophia__message">
            I&apos;m here to help you turn anything you imagine into an unforgettable story.
          </p>
          <div className="idea-sophia__partner">
            <Sparkles aria-hidden="true" />
            <span>Your creative partner,<br />from first spark to final frame.</span>
          </div>
        </section>
      </aside>

      <section className="idea-composer" aria-labelledby="idea-title">
        <header className="idea-composer__heading">
          <h1 id="idea-title">What do you want to <span>create?</span></h1>
          <p>
            Give me anything. A thought, an image, a scene, a feeling,<br />
            or even something you <em>can&apos;t quite explain yet.</em>
          </p>
          <ChevronDown aria-hidden="true" />
        </header>

        <div className="idea-input-shell">
          <label htmlFor="idea-brief">Add anything...</label>
          <textarea
            id="idea-brief"
            value={idea}
            maxLength={2000}
            onChange={(event) => setIdea(event.target.value)}
            placeholder="Type your idea, speak it, drop an image, sketch or file, or import an existing script."
          />
          <output className="idea-input-shell__count" htmlFor="idea-brief">
            {idea.length} / 2000
          </output>
          <div className="idea-mode-toolbar" aria-label="Idea input methods">
            {ideaModes.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                type="button"
                className={activeMode === id ? "is-active" : undefined}
                aria-pressed={activeMode === id}
                onClick={() => selectMode(id, label)}
              >
                <Icon aria-hidden="true" />
                <span>{label}</span>
              </button>
            ))}
          </div>
        </div>

        <p className="idea-privacy"><LockKeyhole aria-hidden="true" /> Your ideas are private and secure.</p>
        <button
          className="idea-explore"
          type="button"
          disabled={!hasIdea}
          onClick={() =>
            navigateInApp(`/discovery?projectId=${encodeURIComponent(projectId)}&characterId=christopher`)
          }
        >
          Explore this idea <ArrowRight aria-hidden="true" />
        </button>
        <p className="idea-explore-help">
          {hasIdea ? "Your idea is ready to explore with Sophia." : "Share your idea above to begin exploring."}
        </p>
      </section>

      <footer className="idea-insight-strip" aria-label="Creative reassurance">
        <p><Lightbulb aria-hidden="true" /> No idea is too big, too small, too wild or too simple.</p>
        <span aria-hidden="true" />
        <p><Heart aria-hidden="true" /> We&apos;re here to help you bring it to life.</p>
      </footer>

      <p className="idea-status" aria-live="polite">{status}</p>
    </main>
  );
}
