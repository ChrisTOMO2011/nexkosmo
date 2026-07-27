import { Bot, ChevronDown, ExternalLink } from "lucide-react";
import {
  advancedStudios,
  aiTools,
  type StudioNavItem,
} from "../../features/studio/config/navigation";
import { Button } from "../ui";

type LeftSidebarProps = {
  items: readonly StudioNavItem[];
  activeItem: string;
  sectionLabel: string;
  onNavigate: (label: string) => void;
  onPlaceholder: (message: string) => void;
};

export function LeftSidebar({
  items,
  activeItem,
  sectionLabel,
  onNavigate,
  onPlaceholder,
}: LeftSidebarProps) {
  return (
    <aside className="project-sidebar" aria-label="Project navigation">
      <Button
        className="project-selector"
        onClick={() => onPlaceholder("Project selector placeholder opened.")}
      >
        <span className="project-copy">
          <small>PROJECT</small>
          <strong>The Last Dawn</strong>
        </span>
        <ChevronDown aria-hidden="true" />
        <span className="project-thumb" aria-hidden="true" />
      </Button>

      <nav className="sidebar-nav" aria-label={sectionLabel}>
        {items.map(({ label, icon: Icon }) => (
          <Button
            className={`sidebar-nav-item ${activeItem === label ? "is-active" : ""}`}
            key={label}
            onClick={() => onNavigate(label)}
          >
            <Icon aria-hidden="true" />
            <span>{label}</span>
          </Button>
        ))}
      </nav>

      <section className="sidebar-section">
        <h2>AI TOOLS</h2>
        {aiTools.map(({ label, icon: Icon }) => (
          <Button
            className="sidebar-nav-item"
            key={label}
            onClick={() => onPlaceholder(`${label} is ready for integration.`)}
          >
            <Icon aria-hidden="true" />
            <span>{label}</span>
          </Button>
        ))}
      </section>

      <section className="advanced-studios">
        <h2>ADVANCED STUDIOS</h2>
        {advancedStudios.map(({ label, detail, icon: Icon, tone }) => (
          <Button
            className="advanced-studio-item"
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
          </Button>
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
        <Button
          trailingIcon={<ExternalLink aria-hidden="true" />}
          onClick={() => onPlaceholder("AI Copilot is ready for integration.")}
        >
          Ask AI Copilot
        </Button>
      </section>
    </aside>
  );
}
