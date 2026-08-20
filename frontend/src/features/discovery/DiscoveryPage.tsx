import { useRef, useState, type CSSProperties } from "react";
import {
  Camera,
  Check,
  ChevronRight,
  Clock3,
  Info,
  MessageSquare,
  Mic2,
  Plus,
  Play,
  Sparkles,
} from "lucide-react";
import discoveryReference from "../../assets/discovery/discovery-reference.jpeg";
import { TopNavigation } from "../../components/studio/TopNavigation";
import { navigateInApp } from "../../app/navigation";

type DiscoveryStyle = CSSProperties & {
  "--discovery-reference": string;
};

type StoryMoment = {
  id: number;
  duration: string;
  range?: string;
  title?: string;
  description: string;
  scenes?: string;
  shots?: string;
  crop: string;
  suggested?: boolean;
};

const moments: StoryMoment[] = [
  {
    id: 1,
    duration: "≈ 8 min",
    range: "00:00–00:08",
    title: "OPENING",
    description: "A boy wakes up and discovers everyone in his town has stopped moving.",
    scenes: "4 Scenes",
    shots: "12 Shots",
    crop: "opening",
  },
  {
    id: 2,
    duration: "≈ 7 min",
    range: "00:08–00:15",
    description: "What’s the first clue that something is wrong?",
    scenes: "3 Scenes",
    shots: "9 Shots",
    crop: "stairs",
    suggested: true,
  },
  {
    id: 3,
    duration: "≈ 15 min",
    description: "A turning point changes everything.",
    crop: "storm",
  },
  {
    id: 4,
    duration: "≈ 25 min",
    description: "The biggest moment.",
    crop: "sunset",
  },
  {
    id: 5,
    duration: "≈ 15 min",
    description: "How it all ends.",
    crop: "storm-end",
  },
];

export function DiscoveryPage() {
  const [selectedMoment, setSelectedMoment] = useState(1);
  const [notice, setNotice] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const style = {
    "--discovery-reference": `url(${discoveryReference})`,
  } as DiscoveryStyle;
  const routeParams = new URLSearchParams(window.location.search);
  const requestedProjectId = routeParams.get("projectId")?.trim() ?? "";
  const requestedCharacterId = routeParams.get("characterId")?.trim() ?? "";
  const projectId = /^[a-z0-9][a-z0-9_-]{0,127}$/iu.test(requestedProjectId)
    ? requestedProjectId
    : "the-last-dawn";
  const characterId = /^[a-z0-9][a-z0-9_-]{0,127}$/iu.test(
    requestedCharacterId,
  )
    ? requestedCharacterId
    : "christopher";

  function announce(message: string) {
    setNotice(message);
  }

  return (
    <main className="discovery-page" style={style}>
      <div className="discovery-page__ambience" aria-hidden="true" />

      <TopNavigation
        activeStage="discover"
        projectId={projectId}
        characterId={characterId}
        onPlaceholder={announce}
        ariaLabel="Story development progress"
      />

      <section className="discovery-hero" aria-labelledby="discovery-title">
        <div className="discovery-meta">
          <span><Info aria-hidden="true" /> Feature</span>
          <span>Target 100m</span>
          <span>Est. 96–104m</span>
          <button type="button" aria-label="Add project detail"><Plus /></button>
        </div>
        <button className="discovery-preview" type="button" onClick={() => announce("Movie preview is not generated yet.")}>
          <Play aria-hidden="true" /> Preview Movie <ChevronRight aria-hidden="true" />
        </button>
        <h1 id="discovery-title">Let’s discover your story.</h1>
        <p>Add anything you have. I’ll help you shape it.</p>
      </section>

      <section className="discovery-story" aria-label="Story discovery board">
        <aside className="sophia-panel" aria-label="Sophia, your AI Producer">
          <div className="sophia-panel__portrait" aria-hidden="true" />
          <div className="sophia-panel__message">
            <strong>Great opening.</strong>
            <p>Shall we see what happens next, or explore another idea?</p>
            <button type="button" onClick={() => announce("Sophia chat opened.")}>
              <MessageSquare aria-hidden="true" /> Chat with Sophia
            </button>
          </div>
        </aside>

        <div className="moment-deck">
          {moments.map((moment) => (
            <StoryCard
              key={moment.id}
              moment={moment}
              selected={selectedMoment === moment.id}
              onSelect={() => setSelectedMoment(moment.id)}
              onBuild={() =>
                navigateInApp(
                  `/discovery/moments/${moment.id}?projectId=${encodeURIComponent(projectId)}&characterId=${encodeURIComponent(characterId)}`,
                )
              }
            />
          ))}
          <button className="moment-deck__next" type="button" aria-label="Show more story moments" onClick={() => announce("More story moments are ready to explore.")}>
            <ChevronRight />
          </button>
        </div>
      </section>

      <section className="discovery-lower" aria-label="Story overview and input">
        <article className="story-overview">
          <h2><Camera aria-hidden="true" /> STORY OVERVIEW <Info aria-hidden="true" /></h2>
          <dl>
            <div><dt>Total Estimated Runtime</dt><dd>≈ 96–104 min</dd></div>
            <div><dt>Mapped Story Length</dt><dd>≈ 15–20 min</dd></div>
            <div className="story-overview__progress"><dt><span /></dt><dd /></div>
            <div><dt>Sections Completed</dt><dd>2 of 5</dd></div>
            <div className="story-overview__confidence">
              <dt>Confidence</dt>
              <dd><i /><i /><i /><i /><i className="is-off" /><i className="is-off" /></dd>
            </div>
          </dl>
        </article>

        <div className="add-anything">
          <input
            className="visually-hidden"
            ref={fileInputRef}
            type="file"
            aria-label="Add an idea, script, image, reference, or voice file"
            onChange={(event) => announce(event.target.files?.[0] ? `${event.target.files[0].name} is ready to add.` : "")}
          />
          <button className="add-anything__plus" type="button" aria-label="Add anything" onClick={() => fileInputRef.current?.click()}>
            <Plus />
          </button>
          <h2>Add Anything</h2>
          <p>Idea&nbsp; · &nbsp;Script&nbsp; · &nbsp;Image&nbsp; · &nbsp;Reference&nbsp; · &nbsp;Voice</p>
          <span>Tell me, show me, speak it, or drop a file.</span>
          <button className="add-anything__voice" type="button" onClick={() => announce("Voice input is ready when microphone access is connected.")}>
            <Mic2 aria-hidden="true" /> Click to speak
          </button>
        </div>

        <article className="sophia-insight">
          <h2><Sparkles aria-hidden="true" /> SOPHIA’S INSIGHT</h2>
          <p>The opening is strong and intriguing.</p>
          <p>Consider showing the boy’s emotional connection to the town to raise the stakes even higher.</p>
          <button type="button" onClick={() => announce("Sophia’s suggestions are ready.")}>
            <Sparkles aria-hidden="true" /> View Suggestions
          </button>
        </article>
      </section>

      <p className="discovery-live" aria-live="polite">{notice}</p>
    </main>
  );
}

type StoryCardProps = {
  moment: StoryMoment;
  selected: boolean;
  onSelect: () => void;
  onBuild: () => void;
};

function StoryCard({ moment, selected, onSelect, onBuild }: StoryCardProps) {
  const compact = moment.id >= 3;
  return (
    <article
      className={`story-card story-card--${compact ? "compact" : moment.suggested ? "suggested" : "opening"}${selected ? " is-selected" : ""}`}
      aria-label={`Story moment ${moment.id}`}
      onClick={onSelect}
    >
      <header>
        <span className="story-card__number">{moment.id}</span>
        {moment.title && <strong>{moment.title}</strong>}
        {moment.suggested && <strong className="story-card__suggested">SUGGESTED BY SOPHIA <Sparkles aria-hidden="true" /></strong>}
        <small>{moment.duration}</small>
        {selected && <span className="story-card__check"><Check aria-hidden="true" /></span>}
      </header>
      <div className={`story-card__image discovery-crop discovery-crop--${moment.crop}`} aria-hidden="true" />
      <p>{moment.description}</p>
      {moment.id === 1 && <div className="story-card__tags"><span>Mystery</span><span>Small Town</span><span>Supernatural</span><button type="button" aria-label="Add tag"><Plus /></button></div>}
      <div className="story-card__stats">
        {moment.scenes ? <span><Clock3 aria-hidden="true" /> {moment.scenes}</span> : <span><Clock3 aria-hidden="true" /> TBD</span>}
        {moment.shots && <span><MessageSquare aria-hidden="true" /> {moment.shots}</span>}
        {!compact && <span className="story-card__status">{moment.id === 1 ? "Updated 2m ago" : "Draft"}</span>}
      </div>
      <button className="story-card__build" type="button" onClick={(event) => { event.stopPropagation(); onBuild(); }}>
        Build this moment {!compact && <ChevronRight aria-hidden="true" />}
      </button>
    </article>
  );
}
