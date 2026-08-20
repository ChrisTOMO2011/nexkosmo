import {
  AlignCenter,
  AlignLeft,
  AlignRight,
  ArrowLeft,
  BookOpen,
  Bot,
  ChevronDown,
  ChevronLeft,
  Clock3,
  Expand,
  Film,
  Grid2X2,
  LockKeyhole,
  MessageSquare,
  Music2,
  Pause,
  Play,
  Plus,
  Save,
  Sparkles,
  Star,
  ThumbsDown,
  ThumbsUp,
  Volume2,
  WandSparkles,
  Wrench,
} from "lucide-react";
import { useState, type CSSProperties, type ReactNode } from "react";
import { navigateInApp } from "../../../app/navigation";
import scriptReference from "../../../assets/shape/script-page-reference.jpeg";
import { TopNavigation } from "../../../components/studio";
import { Toast } from "../../../components/ui";

type ScriptLine = {
  number: number;
  text: string;
  tone?: "heading" | "character" | "dialogue" | "transition";
  selected?: boolean;
  indent?: "character" | "dialogue";
};

const scriptLines: ScriptLine[] = [
  { number: 1, text: "INT. BEDROOM – EARLY MORNING", tone: "heading" },
  { number: 2, text: "FADE IN:", tone: "transition" },
  { number: 3, text: "The pale morning light filters through thin curtains." },
  { number: 4, text: "A digital alarm clock reads 07:12." },
  { number: 5, text: "" },
  { number: 6, text: "JACK (17) sits up, disoriented. The room is small," },
  { number: 7, text: "posters peeling at the corners." },
  { number: 8, text: "" },
  { number: 9, text: "The clock BUZZES." },
  { number: 10, text: "ALARM CLOCK (V.O.)", tone: "character", indent: "character" },
  { number: 11, text: "Time to wake up.", tone: "dialogue", indent: "dialogue" },
  { number: 12, text: "" },
  { number: 13, text: "Jack reaches out and slaps the clock. Silence." },
  { number: 14, text: "JACK", tone: "character", indent: "character" },
  { number: 15, text: "Not today.", tone: "dialogue", indent: "dialogue", selected: true },
  { number: 16, text: "" },
  { number: 17, text: "He swings his legs off the bed." },
  { number: 18, text: "" },
  { number: 19, text: "" },
  { number: 20, text: "CUT TO:", tone: "transition" },
];

const outline = [
  { number: "1", title: "OPENING", runtime: "≈ 8 min", active: true },
  { number: "2", title: "THE CALL", runtime: "≈ 15 min", active: false },
  { number: "3", title: "DESCENT", runtime: "≈ 25 min", active: false },
  { number: "4", title: "THE TRUTH", runtime: "≈ 30 min", active: false },
  { number: "5", title: "RESOLUTION", runtime: "≈ 30 min", active: false },
] as const;

const sceneChildren = [
  ["1.1", "Bedroom"],
  ["1.2", "Empty House"],
  ["1.3", "Frozen Street"],
  ["1.4", "Decision to Leave"],
] as const;

const timelineRows = [
  {
    icon: <MessageSquare aria-hidden="true" />,
    label: "Jack (Dialogue)",
    colour: "violet",
    clips: [
      ["8%", "15%", "Not today."],
      ["67%", "26%", "He swings his legs off the bed."],
    ],
  },
  {
    icon: <MessageSquare aria-hidden="true" />,
    label: "Sarah (Dialogue)",
    colour: "pink",
    clips: [
      ["11%", "28%", "(Off) Everything okay?"],
      ["64%", "25%", "I don’t know anymore."],
    ],
  },
  {
    icon: <Film aria-hidden="true" />,
    label: "Scene Direction/Narration",
    colour: "slate",
    clips: [
      ["0%", "21%", "The pale morning light filters through thin curtains."],
      ["22%", "16%", "A digital alarm clock reads 07:12."],
      ["39%", "14%", "Jack sits up, disoriented."],
      ["54%", "18%", "Jack reaches out and slaps the clock."],
      ["73%", "14%", "Silence."],
    ],
  },
  {
    icon: <Music2 aria-hidden="true" />,
    label: "Music",
    colour: "amber",
    clips: [
      ["0%", "35%", "Ambient Pad"],
      ["36%", "31%", "Emotional Build"],
      ["68%", "32%", "Soft Piano"],
    ],
  },
  {
    icon: <Volume2 aria-hidden="true" />,
    label: "Sound Effects",
    colour: "red",
    clips: [
      ["0%", "23%", "Room Tone"],
      ["24%", "19%", "Alarm Clock BUZZ"],
      ["44%", "22%", "Slap / Hit"],
      ["67%", "19%", "Clock Stops"],
    ],
  },
  {
    icon: <Pause aria-hidden="true" />,
    label: "Pause / Timing",
    colour: "blue",
    clips: [
      ["0%", "19%", "2.0 sec"],
      ["20%", "14%", "0.5 sec"],
      ["61%", "14%", "0.5 sec"],
      ["76%", "14%", "1.0 sec"],
    ],
  },
] as const;

const sceneTools = [
  { label: "Dialogue", icon: MessageSquare },
  { label: "Action", icon: Sparkles },
  { label: "Scene", icon: Grid2X2 },
  { label: "Notes", icon: BookOpen },
  { label: "AI Help", icon: Wrench },
] as const;

export function ShapePage({ projectId }: { projectId: string }) {
  const [activeTool, setActiveTool] = useState("Dialogue");
  const [status, setStatus] = useState("");
  const [playing, setPlaying] = useState(false);
  const [timelineVisible, setTimelineVisible] = useState(true);
  const [suggestionApplied, setSuggestionApplied] = useState(false);

  const announce = (message: string) => {
    setStatus("");
    requestAnimationFrame(() => setStatus(message));
  };

  const referenceStyle = {
    "--script-reference": `url(${scriptReference})`,
  } as CSSProperties;

  return (
    <div className="nexkosmo-studio script-workspace" style={referenceStyle}>
      <TopNavigation
        activeStage="shape"
        projectId={projectId}
        onPlaceholder={announce}
      />
      <p className="script-workspace__tagline">Shape your story. Perfect the script.</p>
      <h1 className="visually-hidden">SHAPE</h1>

      <div className="script-workspace__shell">
        <aside className="script-sidebar" aria-label="Movie Map outline">
          <button
            className="script-back"
            type="button"
            onClick={() =>
              navigateInApp(
                `/discovery?projectId=${encodeURIComponent(projectId)}&characterId=christopher`,
              )
            }
          >
            <ArrowLeft aria-hidden="true" /> Back to Movie Map
          </button>

          <section className="script-project-card" aria-labelledby="script-project-title">
            <div className="script-project-card__heading">
              <span className="script-project-art" aria-hidden="true" />
              <span>
                <strong id="script-project-title">THE LOST STAR</strong>
                <small>Feature Film</small>
              </span>
            </div>
            <dl>
              <div><dt>Runtime</dt><dd>108 min</dd></div>
              <div><dt>Scenes</dt><dd>42</dd></div>
              <div><dt>Script Pages</dt><dd>112</dd></div>
            </dl>
            <header className="script-outline-title">
              <span>MOVIE MAP OUTLINE</span>
              <button type="button" onClick={() => announce("Movie Map outline editing opened.")}>
                <WandSparkles aria-hidden="true" /> Edit
              </button>
            </header>
            <nav aria-label="Movie Map sections">
              {outline.map((section) => (
                <div key={section.number}>
                  <button
                    type="button"
                    className={section.active ? "is-active" : ""}
                    onClick={() => announce(`${section.title} selected.`)}
                  >
                    <span>{section.number}</span>
                    <strong>{section.title}</strong>
                    <small>{section.runtime}</small>
                  </button>
                  {section.active && (
                    <div className="script-outline-children">
                      {sceneChildren.map(([number, title], index) => (
                        <button
                          type="button"
                          key={number}
                          className={index === 0 ? "is-selected" : ""}
                          onClick={() => announce(`${title} scene selected.`)}
                        >
                          <span>{number}</span>{title}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </nav>
            <button className="script-add-moment" type="button" onClick={() => announce("Add Moment opened.")}>
              <Plus aria-hidden="true" /> Add Moment
            </button>
          </section>

          <section className="script-map-card" aria-labelledby="movie-map-title">
            <span>
              <strong id="movie-map-title">MOVIE MAP</strong>
              <small>Your story structure</small>
              <button type="button" aria-label="Previous Movie Map card"><ChevronLeft aria-hidden="true" /></button>
            </span>
            <button className="script-map-moment" type="button" onClick={() => navigateInApp(`/discovery/moments/1?projectId=${encodeURIComponent(projectId)}&characterId=christopher`)}>
              <span><strong>1&nbsp;&nbsp; OPENING</strong><small>≈ 8 min</small></span>
              <i aria-hidden="true" />
              <span><small>4 Scenes&nbsp; · &nbsp;12 Shots</small><b aria-hidden="true" /></span>
            </button>
          </section>
        </aside>

        <main className="script-main" aria-label="Script workspace">
          <section className="screenplay-editor" aria-labelledby="screenplay-title">
            <header className="screenplay-editor__header">
              <button type="button" id="screenplay-title" onClick={() => announce("Scene chooser opened.")}>
                Scene 1&nbsp; · &nbsp;Bedroom <ChevronDown aria-hidden="true" />
              </button>
              <span><Clock3 aria-hidden="true" /> 108 min</span>
              <button className="script-preview" type="button" onClick={() => { setPlaying((value) => !value); announce(playing ? "Scene preview paused." : "Scene preview started."); }}>
                {playing ? <Pause aria-hidden="true" /> : <Play aria-hidden="true" />} Preview Scene
              </button>
              <button className="script-more" type="button" aria-label="More scene options" onClick={() => announce("Scene options opened.")}>•••</button>
            </header>
            <div className="screenplay-editor__meta">
              <span>1 of 8</span><span>3 pages</span>
              <button type="button" aria-label="Toggle cards" onClick={() => announce("Script card view toggled.")}><Grid2X2 aria-hidden="true" /></button>
              <button type="button" aria-label="Expand script" onClick={() => announce("Script editor expanded.")}><Expand aria-hidden="true" /></button>
              <button type="button" aria-label="More script controls"><ChevronDown aria-hidden="true" /></button>
            </div>
            <div className="screenplay-editor__paper" role="textbox" aria-multiline="true" aria-label="Screenplay editor" tabIndex={0}>
              {scriptLines.map((line) => (
                <div className={`script-line ${line.selected ? "is-selected" : ""}`} key={line.number}>
                  <span className="script-line__number">{line.number}</span>
                  <span className={`script-line__text ${line.tone ? `is-${line.tone}` : ""} ${line.indent ? `is-indent-${line.indent}` : ""}`.trim()}>
                    {line.text || "\u00a0"}
                  </span>
                </div>
              ))}
              <i className="screenplay-scroll" aria-hidden="true" />
            </div>
            <footer className="screenplay-toolbar" aria-label="Script formatting">
              <button type="button">Action <ChevronDown aria-hidden="true" /></button>
              <FormatButton label="Bold"><strong>B</strong></FormatButton>
              <FormatButton label="Italic"><em>I</em></FormatButton>
              <FormatButton label="Underline"><u>U</u></FormatButton>
              <FormatButton label="Strikethrough"><s>S</s></FormatButton>
              <FormatButton label="Align left"><AlignLeft aria-hidden="true" /></FormatButton>
              <FormatButton label="Align center"><AlignCenter aria-hidden="true" /></FormatButton>
              <FormatButton label="Align right"><AlignRight aria-hidden="true" /></FormatButton>
              <button type="button" className="screenplay-toolbar__type">Dialogue <ChevronDown aria-hidden="true" /></button>
              <button type="button" aria-label="Keyboard shortcuts"><Grid2X2 aria-hidden="true" /></button>
            </footer>
          </section>

          <section className={`script-timeline ${timelineVisible ? "" : "is-collapsed"}`} aria-label="Scene timeline">
            <header>
              <strong>SCENE TIMELINE</strong><span>≈ 00:30</span><span>6 Layers</span>
              <button type="button" onClick={() => setTimelineVisible((value) => !value)}>{timelineVisible ? "Hide Timeline" : "Show Timeline"} <ChevronDown aria-hidden="true" /></button>
              <span className="script-timeline__snap">Snap&nbsp;&nbsp; − <input aria-label="Timeline zoom" type="range" min="0" max="100" defaultValue="60" /> + <Expand aria-hidden="true" /></span>
            </header>
            {timelineVisible && (
              <div className="script-timeline__body">
                <div className="script-time-ruler" aria-hidden="true">
                  {['00:00','00:05','00:10','00:15','00:25'].map((time) => <span key={time}>{time}</span>)}
                </div>
                <div className="script-playhead" aria-hidden="true"><span>00:07</span></div>
                {timelineRows.map((row) => (
                  <div className="script-track" key={row.label}>
                    <div className={`script-track__label is-${row.colour}`}>
                      {row.icon}<span>{row.label}</span>
                      <button type="button" aria-label={`Solo ${row.label}`}>S</button>
                      <button type="button" aria-label={`Mute ${row.label}`}>M</button>
                      <LockKeyhole aria-label={`${row.label} locked`} />
                    </div>
                    <div className="script-track__lane">
                      {row.clips.map(([left, width, label]) => (
                        <button
                          className={`script-clip is-${row.colour}`}
                          type="button"
                          key={`${left}-${label}`}
                          style={{ left, width }}
                          onClick={() => announce(`${label} selected in the timeline.`)}
                        >
                          {label}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </main>

        <aside className="script-inspector" aria-label="Script inspector">
          <section className="script-sophia-card" aria-labelledby="script-sophia-title">
            <header>
              <span className="script-sophia-avatar" aria-hidden="true" />
              <span><strong id="script-sophia-title">SOPHIA</strong><small>AI Producer</small><i aria-hidden="true" /></span>
              <em>●&nbsp; Online</em>
            </header>
            <div className="script-wave" aria-hidden="true" />
            <p>This opening is strong. Jack’s reluctant tone establishes his emotional state.</p>
            <p>Would you like to deepen the reason he doesn’t want to get up?</p>
            <footer>
              <button type="button" className="is-primary" onClick={() => announce("Sophia’s suggestions opened.")}><Sparkles aria-hidden="true" /> Suggestions</button>
              <button type="button" onClick={() => announce("Ask Sophia opened.")}><Star aria-hidden="true" /> Ask Anything</button>
            </footer>
          </section>

          <section className="script-scene-tools" aria-labelledby="scene-tools-title">
            <h2 id="scene-tools-title">SCENE TOOLS</h2>
            <div className="script-tool-tabs" role="tablist" aria-label="Scene tools">
              {sceneTools.map(({ label, icon: Icon }) => (
                <button
                  type="button"
                  role="tab"
                  aria-selected={activeTool === label}
                  className={activeTool === label ? "is-active" : ""}
                  onClick={() => setActiveTool(label)}
                  key={label}
                >
                  <Icon aria-hidden="true" />{label}
                </button>
              ))}
            </div>
            {activeTool === "Dialogue" ? (
              <div className="script-dialogue-controls">
                <h3>DIALOGUE CONTROLS</h3>
                <label>Voice<select defaultValue="Jack (Young)"><option>Jack (Young)</option><option>Jack (Adult)</option></select></label>
                <label>Performance<select defaultValue="Resigned"><option>Resigned</option><option>Hopeful</option><option>Uneasy</option></select></label>
                <label>Tone<select defaultValue="Natural"><option>Natural</option><option>Intimate</option><option>Dramatic</option></select></label>
                <button type="button" className="script-voice-play" aria-label="Play dialogue voice" onClick={() => announce("Dialogue voice preview started.")}><Play aria-hidden="true" /></button>
                <div className="script-dialogue-wave" aria-hidden="true" /><time>00:00 / 00:03</time>
                <div className="script-ai-suggestion">
                  <h3>AI SUGGESTION</h3>
                  <p>Consider adding a small action here that shows Jack’s internal conflict.</p>
                  <button type="button" onClick={() => { setSuggestionApplied(true); announce("AI suggestion applied to the scene."); }}>{suggestionApplied ? "Applied" : "Apply"}</button>
                  <button type="button" aria-label="Like suggestion"><ThumbsUp aria-hidden="true" /></button>
                  <button type="button" aria-label="Dislike suggestion"><ThumbsDown aria-hidden="true" /></button>
                </div>
              </div>
            ) : (
              <div className="script-tool-placeholder">
                <Bot aria-hidden="true" />
                <strong>{activeTool}</strong>
                <p>{activeTool} controls remain connected to this scene and will appear here.</p>
              </div>
            )}
          </section>
        </aside>
      </div>

      <footer className="script-statusbar">
        <span>Auto Save <i aria-hidden="true" /> On</span>
        <span><Save aria-hidden="true" /> Saved 2 min ago</span>
        <span>Single click = Select layer&nbsp;&nbsp; · &nbsp;&nbsp;Double click = Edit layer</span>
      </footer>
      <Toast key={status} message={status} />
    </div>
  );
}

function FormatButton({ label, children }: { label: string; children: ReactNode }) {
  return <button type="button" aria-label={label}>{children}</button>;
}
