import { useState, type CSSProperties } from "react";
import {
  AlarmClock,
  ArrowLeft,
  Bookmark,
  Camera,
  ChevronDown,
  Crosshair,
  Focus,
  Grid2X2,
  Lightbulb,
  List,
  MessageSquare,
  MoreHorizontal,
  Move,
  Music2,
  Play,
  Plus,
  Redo2,
  RotateCw,
  Scan,
  Sparkles,
  Sun,
  Undo2,
  UserRound,
  Volume2,
  WandSparkles,
  ZoomIn,
  type LucideIcon,
} from "lucide-react";
import referenceImage from "../../assets/discovery/build-moment-reference.jpeg";
import { TopNavigation } from "../../components/studio/TopNavigation";
import { navigateInApp } from "../../app/navigation";

type MomentStyle = CSSProperties & {
  "--moment-reference": string;
};

type Tool = {
  label: string;
  icon: LucideIcon;
};

const tools: Tool[] = [
  { label: "Select", icon: Crosshair },
  { label: "Move", icon: Move },
  { label: "Rotate", icon: RotateCw },
  { label: "Scale", icon: Scan },
  { label: "Focus", icon: Focus },
  { label: "Grid", icon: Grid2X2 },
  { label: "Snap", icon: Sparkles },
  { label: "More", icon: MoreHorizontal },
];

const inspectorTabs: Tool[] = [
  { label: "Scene", icon: Grid2X2 },
  { label: "Character", icon: UserRound },
  { label: "Light", icon: Sun },
  { label: "Camera", icon: Camera },
  { label: "Props", icon: AlarmClock },
];

const shots = [
  { id: "1.1.1", time: "00:04", title: "Alarm clock close up", detail: "CU · Static", crop: "clock" },
  { id: "1.1.2", time: "00:06", title: "Jack sits up", detail: "WS · Static", crop: "sits" },
  { id: "1.1.3", time: "00:05", title: "Looks toward window", detail: "MS · Static", crop: "window" },
  { id: "1.1.4", time: "00:07", title: "Sees someone frozen", detail: "OS · Static", crop: "figure" },
  { id: "1.1.5", time: "00:06", title: "Jack reacts", detail: "CU · Static", crop: "reacts" },
  { id: "1.1.6", time: "00:05", title: "Push in slowly", detail: "WS · Push In", crop: "room" },
] as const;

const sceneList = [
  ["1.1", "Bedroom", "≈ 2 min"],
  ["1.2", "Empty House", "≈ 2 min"],
  ["1.3", "Frozen Street", "≈ 3 min"],
  ["1.4", "Decision to Leave", "≈ 1 min"],
] as const;

export function MomentWorkspacePage({ momentId }: { momentId: string }) {
  const params = new URLSearchParams(window.location.search);
  const projectId = safeRouteValue(params.get("projectId"), "the-last-dawn");
  const characterId = safeRouteValue(params.get("characterId"), "christopher");
  const [activeTool, setActiveTool] = useState("Select");
  const [activeInspector, setActiveInspector] = useState("Scene");
  const [activeMood, setActiveMood] = useState("Mystery");
  const [selectedShot, setSelectedShot] = useState("1.1.1");
  const [snapEnabled, setSnapEnabled] = useState(true);
  const [notice, setNotice] = useState("");
  const style = {
    "--moment-reference": `url(${referenceImage})`,
  } as MomentStyle;

  const movieMapHref = `/discovery?projectId=${encodeURIComponent(projectId)}&characterId=${encodeURIComponent(characterId)}`;

  return (
    <main className="moment-workspace" style={style}>
      <TopNavigation
        activeStage="discover"
        projectId={projectId}
        characterId={characterId}
        onPlaceholder={setNotice}
        ariaLabel="Story development progress"
      />

      <section className="moment-context" aria-label="Current story moment">
        <button
          type="button"
          className="moment-back"
          onClick={() => navigateInApp(movieMapHref)}
        >
          <ArrowLeft aria-hidden="true" /> Back to Movie Map
        </button>
        <div className="moment-summary">
          <span className="moment-summary__number">{momentId}</span>
          <span className="moment-summary__copy">
            <strong>OPENING</strong>
            <small>A boy wakes up and discovers everyone in his town has stopped moving.</small>
          </span>
          <span className="moment-summary__duration">≈ 8 min</span>
          <time>00:00:00 – 00:08:00</time>
          <button type="button" onClick={() => setNotice("Moment preview is ready when rendering is connected.")}>
            <Play aria-hidden="true" /> Preview This Moment
          </button>
        </div>
        <div className="moment-project-meta">
          <span>Feature</span><i />
          <span>Target 100m</span><i />
          <span>Est. 96–104m</span>
        </div>
      </section>

      <section className="moment-stage" aria-label="Moment scene editor">
        <div className="moment-canvas" aria-label="Opening bedroom scene">
          <div className="moment-canvas__shade" aria-hidden="true" />
        </div>

        <aside className="moment-toolbox" aria-label="Canvas tools">
          {tools.map(({ label, icon: Icon }) => {
            const isSwitch = label === "Grid" || label === "Snap";
            return (
              <button
                type="button"
                className={activeTool === label ? "is-active" : ""}
                aria-pressed={isSwitch ? (label === "Snap" ? snapEnabled : false) : activeTool === label}
                key={label}
                onClick={() => {
                  setActiveTool(label);
                  if (label === "Snap") setSnapEnabled((current) => !current);
                }}
              >
                <Icon aria-hidden="true" />
                <span>{label}</span>
                {isSwitch && <i className={label === "Snap" && snapEnabled ? "is-on" : ""} aria-hidden="true" />}
              </button>
            );
          })}
        </aside>

        <aside className="moment-sophia" aria-label="Sophia, AI Producer">
          <div className="moment-sophia__portrait" aria-hidden="true" />
          <div>
            <strong>Sophia</strong>
            <small>AI Producer</small>
            <p>The morning light sets a perfect mood.</p>
            <p>Would you like to extend the beat before he sees anyone?</p>
            <span>
              <button type="button" onClick={() => setNotice("Sophia's moment options opened.")}>Show Options</button>
              <button type="button" onClick={() => setNotice("Sophia's suggestion dismissed.")}>Not Now</button>
            </span>
          </div>
        </aside>

        <aside className="moment-inspector" aria-label="Moment inspector">
          <div className="moment-inspector__tabs" role="tablist" aria-label="Moment property categories">
            {inspectorTabs.map(({ label, icon: Icon }) => (
              <button
                type="button"
                role="tab"
                aria-selected={activeInspector === label}
                className={activeInspector === label ? "is-active" : ""}
                key={label}
                onClick={() => setActiveInspector(label)}
              >
                <Icon aria-hidden="true" /> {label}
              </button>
            ))}
          </div>
          <div className="moment-inspector__body">
            <h2>{activeInspector.toUpperCase()} CONTROLS</h2>
            {activeInspector === "Scene" ? (
              <>
                <label>Mood</label>
                <div className="moment-pills">
                  {["Mystery", "Uneasy", "Curious"].map((mood) => (
                    <button
                      type="button"
                      className={activeMood === mood ? "is-active" : ""}
                      aria-pressed={activeMood === mood}
                      onClick={() => setActiveMood(mood)}
                      key={mood}
                    >
                      {mood}
                    </button>
                  ))}
                </div>
                <label className="moment-field-label"><span>Time of Day</span><output>07:12 AM</output></label>
                <input aria-label="Time of Day" type="range" min="0" max="24" defaultValue="12" />
                <label className="moment-select">Weather <button type="button">Clear <ChevronDown /></button></label>
                <label className="moment-select">Location <button type="button">Residential Street <ChevronDown /></button></label>
                <button className="moment-add-note" type="button" onClick={() => setNotice("Scene note field opened.")}><Plus /> Add Note</button>
              </>
            ) : (
              <div className="moment-inspector__placeholder">
                <Sparkles aria-hidden="true" />
                <p>{activeInspector} controls remain connected to this moment.</p>
              </div>
            )}
          </div>
        </aside>
      </section>

      <section className="moment-timeline" aria-label="Scenes and shots timeline">
        <div className="moment-transport">
          <button type="button" aria-label="Play moment"><Play /></button>
          <button type="button" aria-label="Undo"><Undo2 /></button>
          <button type="button" aria-label="Redo"><Redo2 /></button>
          <button type="button" aria-label="Add bookmark"><Bookmark /></button>
          <time>00:00:04:07</time>
          <div className="moment-ruler" aria-hidden="true">
            {["00:00", "00:01", "00:02", "00:03", "00:04", "00:05", "00:06", "00:07", "00:08"].map((time) => <span key={time}>{time}</span>)}
          </div>
          <button type="button" aria-label="Zoom out">−</button>
          <input aria-label="Timeline zoom" type="range" min="0" max="100" defaultValue="62" />
          <button type="button" aria-label="Zoom in"><ZoomIn /></button>
          <button type="button">Fit</button>
        </div>

        <div className="moment-timeline__content">
          <aside className="moment-scenes">
            <h2>SCENES & SHOTS <List /></h2>
            <p><span>1. OPENING</span><span>≈ 8 min</span></p>
            {sceneList.map(([number, name, duration]) => (
              <button type="button" className={number === "1.1" ? "is-active" : ""} key={number}>
                <span>{number}</span><strong>{name}</strong><small>{duration}</small>
              </button>
            ))}
            <button type="button" className="moment-scenes__add"><Plus /> Add Scene</button>
          </aside>

          <div className="moment-shots">
            {shots.map((shot) => (
              <button
                type="button"
                className={`moment-shot ${selectedShot === shot.id ? "is-active" : ""}`}
                aria-pressed={selectedShot === shot.id}
                onClick={() => setSelectedShot(shot.id)}
                key={shot.id}
              >
                <span className="moment-shot__heading"><strong>{shot.id}</strong><time>{shot.time}</time></span>
                <span className={`moment-shot__image moment-shot__image--${shot.crop}`} aria-hidden="true" />
                <span className="moment-shot__title">{shot.title}</span>
                <small>{shot.detail}</small>
                <span className="moment-shot__icons" aria-hidden="true"><Camera /><MessageSquare /><Music2 /></span>
              </button>
            ))}
            <button type="button" className="moment-add-shot" onClick={() => setNotice("A new shot placeholder was added.")}><Plus /><span>Add Shot</span></button>
          </div>
        </div>

        <div className="moment-quick-actions" aria-label="Moment creation shortcuts">
          <QuickAction icon={UserRound} label="Add Character" />
          <QuickAction icon={MessageSquare} label="Add Dialogue" />
          <QuickAction icon={AlarmClock} label="Add Prop" />
          <QuickAction icon={Lightbulb} label="Adjust Lighting" />
          <QuickAction icon={Camera} label="Set Camera" />
          <QuickAction icon={Volume2} label="Add Sound" />
          <button type="button" className="is-primary" onClick={() => setNotice("Shot idea generation is not connected yet.")}><WandSparkles /> Generate Shot Ideas</button>
        </div>
      </section>

      <p className="moment-live" role="status" aria-live="polite">{notice}</p>
    </main>
  );
}

function safeRouteValue(value: string | null, fallback: string) {
  return value && /^[a-z0-9][a-z0-9_-]{0,127}$/iu.test(value) ? value : fallback;
}

function QuickAction({ icon: Icon, label }: { icon: LucideIcon; label: string }) {
  return <button type="button"><Icon aria-hidden="true" /> {label}</button>;
}
