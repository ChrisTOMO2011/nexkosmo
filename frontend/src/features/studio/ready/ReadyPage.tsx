import { useState, type CSSProperties } from "react";
import {
  ArrowRight,
  BookOpen,
  Box,
  CalendarCheck,
  Check,
  CheckCircle2,
  CircleDollarSign,
  Clock3,
  Edit3,
  Film,
  Lightbulb,
  MapPin,
  MessageSquare,
  PackageCheck,
  ShieldCheck,
  Sparkles,
  UserRound,
  UsersRound,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { navigateInApp } from "../../../app/navigation";
import projectArt from "../../../assets/ready/project-art.jpg";
import scene38 from "../../../assets/ready/scene-38.jpg";
import scene39 from "../../../assets/ready/scene-39.jpg";
import scene40 from "../../../assets/ready/scene-40.jpg";
import scene41 from "../../../assets/ready/scene-41.jpg";
import scene42 from "../../../assets/ready/scene-42.jpg";
import sophiaPortrait from "../../../assets/idea/sophia-transparent.png";
import { TopNavigation } from "../../../components/studio";

type ReadyStyle = CSSProperties & {
  "--ready-project-art": string;
  "--ready-scene-38": string;
  "--ready-scene-39": string;
  "--ready-scene-40": string;
  "--ready-scene-41": string;
  "--ready-scene-42": string;
};

type ReadinessCheck = {
  label: string;
  detail: string;
  icon: LucideIcon;
};

const readinessChecks: ReadinessCheck[] = [
  {
    label: "Story & Script",
    detail: "Screenplay locked. Scenes resolved. Dialogue finalized.",
    icon: BookOpen,
  },
  {
    label: "Characters & Performance",
    detail: "All characters defined, looks approved, performance notes set.",
    icon: UserRound,
  },
  {
    label: "World & Assets",
    detail: "Environments, props, vehicles and key assets prepared.",
    icon: PackageCheck,
  },
  {
    label: "Continuity",
    detail: "Timeline, character state, props, locations and events consistent.",
    icon: Film,
  },
  {
    label: "Rights & Provenance",
    detail: "Licenses, permissions and provenance verified.",
    icon: ShieldCheck,
  },
  {
    label: "Production Plan",
    detail: "Scenes planned, shots estimated, resources and schedule set.",
    icon: CalendarCheck,
  },
];

const scenePreviews = [
  { number: 38, title: "The Signal" },
  { number: 39, title: "Into the Unknown" },
  { number: 40, title: "The Choice" },
  { number: 41, title: "The Confrontation" },
  { number: 42, title: "A New Beginning" },
] as const;

const projectFacts = [
  { label: "Runtime", value: "108 min", icon: Clock3 },
  { label: "Scenes", value: "42", icon: Film },
  { label: "Script Pages", value: "112", icon: BookOpen },
  { label: "Characters", value: "8", icon: UsersRound },
  { label: "Locations", value: "14", icon: MapPin },
  { label: "Assets", value: "37", icon: Box },
  { label: "Est. Shots", value: "≈186", icon: Film },
  { label: "Budget Range", value: "Mid", icon: CircleDollarSign },
] as const;

export function ReadyPage({ projectId }: { projectId: string }) {
  const [selectedScene, setSelectedScene] = useState(42);
  const [status, setStatus] = useState("");
  const style = {
    "--ready-project-art": `url(${projectArt})`,
    "--ready-scene-38": `url(${scene38})`,
    "--ready-scene-39": `url(${scene39})`,
    "--ready-scene-40": `url(${scene40})`,
    "--ready-scene-41": `url(${scene41})`,
    "--ready-scene-42": `url(${scene42})`,
  } as ReadyStyle;

  return (
    <main className="ready-page" style={style}>
      <TopNavigation
        activeStage="ready"
        projectId={projectId}
        characterId="christopher"
        onPlaceholder={setStatus}
        ariaLabel="Creator workflow"
      />

      <section className="ready-dashboard" aria-labelledby="ready-page-title">
        <ProjectSummary onAction={setStatus} />

        <section className="ready-center">
          <header className="ready-heading">
            <h1 id="ready-page-title">Ready to bring it to life?</h1>
            <p>Sophia and Brain have completed their final checks.</p>
          </header>

          <ReadinessResults />

          <ScenePreviewStrip
            selectedScene={selectedScene}
            onSelect={(scene) => {
              setSelectedScene(scene);
              setStatus(`Scene ${scene} selected for preview.`);
            }}
            onViewAll={() => setStatus("The complete scene overview is ready for review.")}
          />
        </section>

        <SophiaReadyPanel onAction={setStatus} />

        <div className="ready-lower">
          <ProductionPackage onAction={setStatus} />
          <DynamicEstimates />
        </div>

        <ProductionHandoff
          onStart={() =>
            navigateInApp(`/studio/projects/${encodeURIComponent(projectId)}/studio`)
          }
        />
      </section>

      <p className="ready-live" aria-live="polite">{status}</p>
    </main>
  );
}

function ProjectSummary({ onAction }: { onAction: (message: string) => void }) {
  return (
    <aside className="ready-project-card" aria-labelledby="ready-project-title">
      <div className="ready-project-art" role="img" aria-label="A young hero beneath a shooting star" />
      <div className="ready-project-copy">
        <h2 id="ready-project-title">THE LOST STAR <Edit3 aria-hidden="true" /></h2>
        <p>Feature Film <span>•</span> Sci-Fi / Adventure</p>
        <dl>
          {projectFacts.map(({ label, value, icon: Icon }, index) => (
            <div key={label} className={index === 3 ? "ready-project-divider" : undefined}>
              <dt><Icon aria-hidden="true" /> {label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
        <button type="button" onClick={() => onAction("Project overview opened.")}>View Project Overview <ArrowRight aria-hidden="true" /></button>
      </div>
    </aside>
  );
}

function ReadinessResults() {
  return (
    <section className="ready-results" aria-labelledby="ready-results-title">
      <header>
        <Check aria-hidden="true" />
        <div>
          <h2 id="ready-results-title">READY FOR PRODUCTION</h2>
          <p>All mandatory checks passed.<br />Your movie is ready when you are.</p>
        </div>
      </header>
      <ul>
        {readinessChecks.map(({ label, detail, icon: Icon }) => (
          <li key={label}>
            <Icon className="ready-results__icon" aria-hidden="true" />
            <div><strong>{label}</strong><span>{detail}</span></div>
            <b>READY</b>
            <CheckCircle2 aria-label="Passed" />
          </li>
        ))}
      </ul>
    </section>
  );
}

function ScenePreviewStrip({
  selectedScene,
  onSelect,
  onViewAll,
}: {
  selectedScene: number;
  onSelect: (scene: number) => void;
  onViewAll: () => void;
}) {
  return (
    <section className="ready-scenes" aria-labelledby="ready-scenes-title">
      <header>
        <h2 id="ready-scenes-title">SCENE PREVIEW (PREVIS / STORYBOARD)</h2>
        <button type="button" onClick={onViewAll}>View All Scenes <ArrowRight aria-hidden="true" /></button>
      </header>
      <div className="ready-scenes__grid">
        {scenePreviews.map((scene) => (
          <button
            key={scene.number}
            type="button"
            className={selectedScene === scene.number ? "is-selected" : undefined}
            aria-pressed={selectedScene === scene.number}
            onClick={() => onSelect(scene.number)}
          >
            <span className={`ready-scene-image ready-scene-image--${scene.number}`} />
            <small>Scene {scene.number}</small>
            <strong>{scene.title}</strong>
          </button>
        ))}
      </div>
    </section>
  );
}

function SophiaReadyPanel({ onAction }: { onAction: (message: string) => void }) {
  return (
    <aside className="ready-sophia" aria-labelledby="ready-sophia-title">
      <header>
        <div><Sparkles aria-hidden="true" /><h2 id="ready-sophia-title">SOPHIA</h2></div>
        <span><i /> Online</span>
        <p>AI Producer</p>
      </header>
      <img src={sophiaPortrait} alt="Sophia, AI Producer" />
      <blockquote>
        <b>“</b>
        <p>Everything checks out.<br />We&apos;re ready when<br />you are, Director.</p>
        <cite>— Sophia</cite>
      </blockquote>
      <div className="ready-sophia__actions">
        <button type="button" onClick={() => onAction("Sophia is ready to explain every completed check.")}><Lightbulb aria-hidden="true" /> Explain Why These Passed</button>
        <button type="button" onClick={() => onAction("Sophia messaging opened.")}><MessageSquare aria-hidden="true" /> Message Sophia</button>
      </div>
    </aside>
  );
}

function ProductionPackage({ onAction }: { onAction: (message: string) => void }) {
  const items = [
    [Film, "42", "Scenes"],
    [CalendarCheck, "≈186", "Shots"],
    [UsersRound, "8", "Characters"],
    [MapPin, "14", "Locations"],
    [Box, "37", "Assets"],
    [CheckCircle2, "", "All Checks Passed"],
  ] as const;

  return (
    <section className="ready-package" aria-labelledby="ready-package-title">
      <header><h2 id="ready-package-title">PRODUCTION PACKAGE</h2><p>Everything you need to start production.</p></header>
      <div>
        {items.map(([Icon, value, label]) => (
          <span key={label}><Icon aria-hidden="true" /><b>{value}</b><small>{label}</small></span>
        ))}
      </div>
      <button type="button" onClick={() => onAction("Full production package opened.")}>View Full Production Package <ArrowRight aria-hidden="true" /></button>
    </section>
  );
}

function DynamicEstimates() {
  return (
    <section className="ready-estimates" aria-labelledby="ready-estimates-title">
      <header><h2 id="ready-estimates-title">ESTIMATES (DYNAMIC)</h2><p>Estimates update based on route, complexity, quality target and available resources.</p></header>
      <div>
        <span><Clock3 aria-hidden="true" /><small>Est. Runtime</small><b>96–104 min</b></span>
        <span><CircleDollarSign aria-hidden="true" /><small>Est. Render Range</small><b>4.2K–5.6K</b><em>Credits</em></span>
        <span><PackageCheck aria-hidden="true" /><small>Production Route</small><b>Hybrid</b><em>Preview-First</em></span>
        <span><Clock3 aria-hidden="true" /><small>Est. Time</small><b>~2–4 weeks</b><em>(Varies by scale)</em></span>
      </div>
      <p>ⓘ Estimates are dynamic and will refine in Production.</p>
    </section>
  );
}

function ProductionHandoff({ onStart }: { onStart: () => void }) {
  return (
    <section className="ready-handoff" aria-labelledby="ready-handoff-title">
      <p>NEXT STAGE</p>
      <div><Film aria-hidden="true" /><h2 id="ready-handoff-title">PRODUCTION</h2></div>
      <span>You&apos;ll enter the Production pipeline.<br />Shots will be generated, validated and approved.</span>
      <button type="button" onClick={onStart}>START PRODUCTION <ArrowRight aria-hidden="true" /></button>
      <small>🔒 You can review and approve every step.</small>
    </section>
  );
}
