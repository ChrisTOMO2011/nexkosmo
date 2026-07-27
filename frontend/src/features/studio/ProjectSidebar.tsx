import { Bot, ChevronDown, ExternalLink } from "lucide-react";
import {
  advancedStudios,
  aiTools,
  productionNav,
} from "./pre-production/data";

type ProjectSidebarProps = {
  activeItem: string;
  onNavigate: (label: string) => void;
  onPlaceholder: (message: string) => void;
};

export function ProjectSidebar({
  activeItem,
  onNavigate,
  onPlaceholder,
}: ProjectSidebarProps) {
  return (
    <aside className="project-sidebar" aria-label="Project navigation">
      <button
        className="project-selector"
        type="button"
        onClick={() => onPlaceholder("Project selector placeholder opened.")}
      >
        <span className="project-copy">
          <small>PROJECT</small>
          <strong>The Last Dawn</strong>
        </span>
        <ChevronDown aria-hidden="true" />
        <span className="project-thumb" aria-hidden="true" />
      </button>

      <nav className="sidebar-nav" aria-label="Pre-production sections">
        {productionNav.map(({ label, icon: Icon }) => (
          <button
            className={`sidebar-nav-item ${activeItem === label ? "is-active" : ""}`}
            type="button"
            key={label}
            onClick={() => onNavigate(label)}
          >
            <Icon aria-hidden="true" />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <section className="sidebar-section">
        <h2>AI TOOLS</h2>
        {aiTools.map(({ label, icon: Icon }) => (
          <button
            className="sidebar-nav-item"
            type="button"
            key={label}
            onClick={() => onPlaceholder(`${label} is ready for integration.`)}
          >
            <Icon aria-hidden="true" />
            <span>{label}</span>
          </button>
        ))}
      </section>

      <section className="advanced-studios">
        <h2>ADVANCED STUDIOS</h2>
        {advancedStudios.map(({ label, detail, icon: Icon, tone }) => (
          <button
            className="advanced-studio-item"
            type="button"
            key={label}
            onClick={() => onPlaceholder(`${label} placeholder opened.`)}
          >
            <span className={`studio-icon tone-${tone}`}>
              <Icon aria-hidden="true" />
            </span>
            <span>
              <strong>{label}</strong>
              <small>{detail}</small>
            </span>
          </button>
        ))}
      </section>

      <section className="copilot-card">
        <div className="copilot-heading">
          <span className="bot-orbit">
            <Bot aria-hidden="true" />
          </span>
          <strong>AI COPILOT</strong>
        </div>
        <p>Need ideas for your scene?</p>
        <button
          type="button"
          onClick={() => onPlaceholder("AI Copilot is ready for integration.")}
        >
          Ask AI Copilot
          <ExternalLink aria-hidden="true" />
        </button>
      </section>
    </aside>
  );
}
