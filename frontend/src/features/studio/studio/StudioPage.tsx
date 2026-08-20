import { useState } from "react";
import {
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  BarChart3,
  BrainCircuit,
  Camera,
  Check,
  CheckCircle2,
  Circle,
  Clock3,
  Expand,
  Eye,
  Film,
  Gauge,
  LockKeyhole,
  Maximize2,
  MessageSquare,
  MoreHorizontal,
  Pause,
  Play,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Star,
  Wrench,
  X,
  ZoomIn,
} from "lucide-react";
import shotMain from "../../../assets/production/shot-main.jpg";
import shot01 from "../../../assets/production/shot-01.jpg";
import shot02 from "../../../assets/production/shot-02.jpg";
import shot03 from "../../../assets/production/shot-03.jpg";
import shot04 from "../../../assets/production/shot-04.jpg";
import shot05 from "../../../assets/production/shot-05.jpg";
import shot06 from "../../../assets/production/shot-06.jpg";
import shot07 from "../../../assets/production/shot-07.jpg";
import shot08 from "../../../assets/production/shot-08.jpg";
import sophiaPortrait from "../../../assets/idea/sophia-transparent.png";
import { TopNavigation } from "../../../components/studio";

type ShotStatus = "approved" | "review" | "rendering" | "not-started";

type ProductionShot = {
  number: string;
  image: string;
  status: ShotStatus;
  duration?: string;
  progress?: number;
};

const shots: ProductionShot[] = [
  { number: "01", image: shot01, status: "approved", duration: "2.1s" },
  { number: "02", image: shot02, status: "approved", duration: "3.4s" },
  { number: "03", image: shot03, status: "review", duration: "3.2s" },
  { number: "04", image: shot04, status: "rendering", duration: "4.0s", progress: 62 },
  { number: "05", image: shot05, status: "not-started" },
  { number: "06", image: shot06, status: "not-started" },
  { number: "07", image: shot07, status: "not-started" },
  { number: "08", image: shot08, status: "not-started" },
];

const productionSections = [
  ["01", "Opening", "3/3", "complete"],
  ["02", "The Call", "5/5", "complete"],
  ["03", "Departure", "4/4", "complete"],
  ["04", "The Journey", "6/7", "warning"],
  ["05", "The Confrontation", "3/8", "warning"],
  ["06", "The Truth", "6/6", "complete"],
  ["07", "The Final Stand", "5/5", "complete"],
  ["08", "Resolution", "4/4", "empty"],
] as const;

const validationChecks = [
  ["Technical Render", "PASS", "pass"],
  ["Character Identity", "PASS", "pass"],
  ["Camera Intent", "PASS", "pass"],
  ["Wardrobe Continuity", "WARNING", "warning"],
  ["Environment", "PASS", "pass"],
  ["Lighting & Shadows", "PASS", "pass"],
  ["Timing & Performance", "PASS", "pass"],
] as const;

export function StudioPage({ projectId }: { projectId: string }) {
  const [selectedShot, setSelectedShot] = useState("03");
  const [reviewMode, setReviewMode] = useState<"Draft" | "Review" | "Final">("Review");
  const [status, setStatus] = useState("");

  return (
    <main className="production-page">
      <TopNavigation
        activeStage="production"
        projectId={projectId}
        characterId="christopher"
        onPlaceholder={setStatus}
        ariaLabel="Creator workflow"
      />

      <section className="production-workspace" aria-labelledby="production-title">
        <ProductionNavigator onAction={setStatus} />

        <section className="production-main">
          <ProductionOverview />
          <ShotReviewPlayer
            selectedShot={selectedShot}
            reviewMode={reviewMode}
            onModeChange={setReviewMode}
            onAction={setStatus}
          />
          <ShotStrip
            selectedShot={selectedShot}
            onSelect={(shot) => {
              setSelectedShot(shot);
              setStatus(`Shot ${shot} selected.`);
            }}
            onAction={setStatus}
          />
          <ProductionTimeline />
        </section>

        <SophiaProductionPanel onAction={setStatus} />

        <ProductionBottomBar onAction={setStatus} />
        <ProductionPrinciples />
      </section>

      <p className="production-live" aria-live="polite">{status}</p>
    </main>
  );
}

function ProductionNavigator({ onAction }: { onAction: (message: string) => void }) {
  return (
    <aside className="production-navigator" aria-labelledby="production-navigator-title">
      <section className="production-nav-scenes">
        <h2 id="production-navigator-title">PRODUCTION NAVIGATOR</h2>
        <div className="production-nav-selector"><span>Movie Overview</span><span>42 Scenes</span></div>
        <ol>
          {productionSections.map(([number, label, count, state]) => (
            <li key={number} className={number === "05" ? "is-open" : undefined}>
              <button type="button" onClick={() => onAction(`${label} selected in Production Navigator.`)}>
                <b>{number}</b><span>{label}</span><small>{count}</small>
                {state === "complete" ? <CheckCircle2 aria-label="Complete" /> : state === "warning" ? <i className="is-warning" aria-label="In production" /> : <Circle aria-label="Not started" />}
              </button>
              {number === "05" && (
                <ul>
                  <li className="is-selected"><button type="button" onClick={() => onAction("Scene 20 Rooftop Chase selected.")}><span>Scene 20</span><b>Rooftop Chase</b><i /></button></li>
                  {[["21", "The Interrogation"], ["22", "Betrayal"], ["23", "Escape"], ["24", "Aftermath"], ["25", "Cliffhanger"]].map(([scene, name]) => (
                    <li key={scene}><button type="button" onClick={() => onAction(`Scene ${scene} ${name} selected.`)}><span>Scene {scene}</span><b>{name}</b><Circle /></button></li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ol>
        <button className="production-overview-button" type="button" onClick={() => onAction("Production overview opened.")}><BarChart3 /> Production Overview</button>
      </section>

      <section className="production-progress" aria-labelledby="movie-progress-title">
        <h2 id="movie-progress-title">MOVIE PROGRESS</h2>
        <div className="production-progress-ring"><strong>29%</strong><small>COMPLETE</small></div>
        <ul>
          <li><i className="is-complete" /> 12 Completed</li>
          <li><i className="is-production" /> 3 In Production</li>
          <li><i className="is-review" /> 2 Need Review</li>
          <li><i className="is-empty" /> 25 Not Started</li>
        </ul>
      </section>

      <section className="production-tip">
        <h2><Sparkles /> TIP FROM SOPHIA</h2>
        <p>Focused work in Studio keeps shots clean and speeds up approvals.</p>
        <button type="button" onClick={() => onAction("Sophia's production guidance opened.")}>Learn More <ArrowRight /></button>
      </section>
    </aside>
  );
}

function ProductionOverview() {
  const metrics = [
    ["SCENES", "42", "Total", Film],
    ["COMPLETED", "12", "Total", CheckCircle2],
    ["IN PRODUCTION", "3", "", Gauge],
    ["NEED REVIEW", "2", "", AlertCircle],
    ["NOT STARTED", "25", "", Circle],
    ["EST. COMPLETION", "~3–4 weeks", "Varies by scale", Clock3],
  ] as const;
  return (
    <section className="production-overview" aria-labelledby="production-title">
      <header><h1 id="production-title">We&apos;re making your movie.</h1><p>Every shot is crafted, validated, and approved with continuity protected at every step.</p></header>
      <div className="production-metrics">
        {metrics.map(([label, value, note, Icon], index) => (
          <article key={label} className={`production-metric production-metric--${index}`}>
            <Icon aria-hidden="true" /><span><small>{label}</small><strong>{value}</strong>{note && <em>{note}</em>}</span>
          </article>
        ))}
      </div>
    </section>
  );
}

function ShotReviewPlayer({
  selectedShot,
  reviewMode,
  onModeChange,
  onAction,
}: {
  selectedShot: string;
  reviewMode: "Draft" | "Review" | "Final";
  onModeChange: (mode: "Draft" | "Review" | "Final") => void;
  onAction: (message: string) => void;
}) {
  return (
    <section className="production-player" aria-label={`Shot ${selectedShot} review`}>
      <header>
        <div><b>Scene 20</b><span>•</span><strong>Rooftop Chase</strong><ArrowRight /><span>Shot {selectedShot}</span><em>REVIEW</em></div>
        <div><button type="button" aria-label="Previous shot"><ArrowLeft /></button><span>Shot 03 of 26</span><button type="button" aria-label="Next shot"><ArrowRight /></button><button type="button" onClick={() => onAction("Take comparison opened.")}><Eye /> Compare Takes</button><button type="button" aria-label="Fullscreen"><Maximize2 /></button><button type="button" aria-label="More shot actions"><MoreHorizontal /></button></div>
      </header>
      <div className="production-player-image" style={{ backgroundImage: `url(${shotMain})` }} role="img" aria-label="Christopher on a rain-soaked rooftop at night" />
      <footer>
        <button type="button" aria-label="Play shot" onClick={() => onAction("Shot preview started.")}><Play /></button>
        <button type="button" aria-label="Previous frame"><ArrowLeft /></button>
        <button type="button" aria-label="Pause"><Pause /></button>
        <button type="button" aria-label="Next frame"><ArrowRight /></button>
        <span className="production-timecode">01:12:04 / 02:35:11</span>
        <span className="production-scrubber"><i /></span>
        <div className="production-review-modes" role="group" aria-label="Review mode">
          {(["Draft", "Review", "Final"] as const).map((mode) => <button type="button" key={mode} aria-pressed={reviewMode === mode} onClick={() => onModeChange(mode)}>{mode}</button>)}
        </div>
        <button type="button" aria-label="Capture frame"><Camera /></button>
        <button type="button" aria-label="Player settings"><Settings /></button>
      </footer>
    </section>
  );
}

function ShotStrip({ selectedShot, onSelect, onAction }: { selectedShot: string; onSelect: (shot: string) => void; onAction: (message: string) => void }) {
  return (
    <section className="production-shots" aria-labelledby="production-shots-title">
      <header><h2 id="production-shots-title">SHOTS IN SCENE 20 <span>(8 SHOTS)</span></h2><button type="button" onClick={() => onAction("All shots opened.")}>View All Shots <ArrowRight /></button></header>
      <div>
        {shots.map((shot) => (
          <button key={shot.number} type="button" className={selectedShot === shot.number ? "is-selected" : undefined} aria-pressed={selectedShot === shot.number} onClick={() => onSelect(shot.number)}>
            <b>{shot.number}</b><img src={shot.image} alt="" />
            {shot.progress ? <span className="production-shot-progress">{shot.progress}%</span> : <span className={`production-shot-state production-shot-state--${shot.status}`}>{shot.status === "approved" ? <CheckCircle2 /> : shot.status === "review" ? <AlertCircle /> : shot.status === "rendering" ? <Gauge /> : <Circle />}{shot.status.replace("-", " ")}</span>}
            {shot.duration && <small>{shot.duration}</small>}
          </button>
        ))}
      </div>
    </section>
  );
}

function ProductionTimeline() {
  const rows = ["Scenes", "Shots", "Rendering", "Review", "Approved"];
  return (
    <section className="production-timeline" aria-labelledby="production-timeline-title">
      <header><h2 id="production-timeline-title">PRODUCTION TIMELINE (OVERVIEW)</h2><button type="button">Expand Timeline <ArrowRight /></button></header>
      <div className="production-timeline-body">
        <div className="production-timeline-labels">{rows.map((row, index) => <span key={row}><i className={`timeline-dot timeline-dot--${index}`} />{row}</span>)}</div>
        <div className="production-timeline-chart">
          <div className="production-scene-numbers">{[15,16,17,18,19,20,21,22,24,25,26].map((scene) => <span key={scene} className={scene === 20 ? "is-current" : undefined}>Scene {scene}</span>)}</div>
          {rows.slice(1).map((row, index) => <div key={row} className={`production-track production-track--${index}`}>{Array.from({ length: index === 2 ? 8 : 10 }, (_, bar) => <i key={bar} />)}</div>)}
          <span className="production-playhead"><b>Scene 20</b></span>
        </div>
        <div className="production-timeline-tools"><button aria-label="Zoom out" type="button"><Search /></button><button aria-label="Zoom in" type="button"><ZoomIn /></button><button aria-label="Expand timeline" type="button"><Expand /></button></div>
      </div>
      <div className="production-timeline-legend"><span className="is-approved">Approved</span><span>In Production</span><span className="is-review">In Production</span><span className="is-warning">Needs Review</span></div>
    </section>
  );
}

function SophiaProductionPanel({ onAction }: { onAction: (message: string) => void }) {
  const actions = [
    ["Review Current Shot", Eye],
    ["Compare Takes", Camera],
    ["Open in Studio", Film],
    ["Repair Issue", Wrench],
    ["Shot Notes", MessageSquare],
    ["Production Status", Camera],
  ] as const;
  return (
    <aside className="production-sophia" aria-labelledby="production-sophia-title">
      <section className="production-sophia-profile">
        <header><div><Sparkles /><h2 id="production-sophia-title">SOPHIA</h2></div><span><i /> Online</span><p>AI Producer</p></header>
        <img src={sophiaPortrait} alt="Sophia, AI Producer" />
        <blockquote><b>“</b><p>Shot 3 looks strong.<br />I found one continuity issue<br />with the jacket.<br />Want me to repair it?</p></blockquote>
      </section>
      <section className="production-validation" aria-labelledby="shot-validation-title">
        <header><h2 id="shot-validation-title">SHOT 03 VALIDATION</h2><ArrowRight /></header>
        <div className="production-blocking"><AlertCircle /><b>1 blocking issue</b><button type="button" onClick={() => onAction("Wardrobe continuity details opened.")}>View Details</button></div>
        <ul>{validationChecks.map(([label, result, state]) => <li key={label} className={state === "warning" ? "is-warning" : undefined}>{state === "pass" ? <CheckCircle2 /> : <AlertCircle />}<span>{label}</span><b>{result}</b></li>)}</ul>
        <p><AlertCircle /> Blocking issue must be resolved<br />before approval.</p>
      </section>
      <section className="production-sophia-actions" aria-labelledby="sophia-actions-title">
        <h2 id="sophia-actions-title">SOPHIA&apos;S ACTIONS</h2>
        {actions.map(([label, Icon]) => <button type="button" key={label} className={label === "Open in Studio" ? "is-primary" : undefined} onClick={() => onAction(`${label} opened.`)}><Icon />{label}{label === "Open in Studio" && <ArrowRight />}</button>)}
      </section>
    </aside>
  );
}

function ProductionBottomBar({ onAction }: { onAction: (message: string) => void }) {
  return (
    <section className="production-bottom" aria-label="Production controls">
      <article className="production-route"><BrainCircuit /><div><h2>PRODUCTION ROUTE</h2><strong>Auto <em>(Recommended)</em></strong><p>The Brain will choose the<br />best production route.</p></div><button type="button" onClick={() => onAction("Production route options opened.")}>Change</button></article>
      <article className="production-estimates"><h2>ESTIMATES (DYNAMIC)</h2><div><span><small>Est. Render Time</small><b>18 min</b></span><span><small>Est. Credits</small><b>240</b></span><span><small>Resolution</small><b>4K</b></span><span><small>Frame Rate</small><b>24 fps</b></span></div><p>ⓘ Estimates update based on route, complexity and queue.</p></article>
      <article className="production-render-status"><h2>RENDER STATUS</h2><div><span><small>Route</small><b>Hybrid (AI + 3D)</b></span><span><small>Est. Time Remaining</small><b>~3 min</b></span><span><small>Est. Credits</small><b>240</b></span><span><small>Quality</small><b>Final</b></span></div><footer><span>● Rendering...</span><button type="button" onClick={() => onAction("Render details opened.")}>Render Details</button></footer></article>
      <article className="production-decision"><h2>READY FOR YOUR DECISION</h2><div><button type="button" className="is-repair" onClick={() => onAction("Repair and revalidation queued as a placeholder action.")}>REPAIR &amp; REVALIDATE <ArrowRight /></button><button type="button" onClick={() => onAction("Repair request opened.")}><Wrench /> Request Repair</button><button type="button" disabled><Check /> APPROVE SHOT<small>Disabled until blocking issues are resolved</small></button><button type="button" className="is-reject" onClick={() => onAction("Reject and regenerate confirmation opened.")}><X /> Reject &amp; Regenerate</button></div></article>
    </section>
  );
}

function ProductionPrinciples() {
  return (
    <footer className="production-principles">
      <span><ShieldCheck /><b>Your story. Your vision.</b><small>Every frame. Built with care.</small></span>
      <span><LockKeyhole /><b>Secure. Private.</b><small>You&apos;re always in control.</small></span>
      <span><Star /><b>Increase Human Agency.</b><small>That&apos;s our North Star.</small></span>
      <span><Sparkles /><b>Sophia and Brain are here to help you succeed.</b></span>
    </footer>
  );
}
