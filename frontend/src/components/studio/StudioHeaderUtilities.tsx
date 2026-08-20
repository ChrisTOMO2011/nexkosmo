import {
  Award,
  Bell,
  Crown,
  Gem,
  Gift,
  Handshake,
  Mail,
  MessageSquare,
  Search,
  Star,
  Trophy,
  UserPlus,
  UserRound,
  UsersRound,
  X,
} from "lucide-react";
import {
  useEffect,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import { Button } from "../ui";

type HeaderPanel =
  | "search"
  | "collaboration"
  | "membership"
  | "notifications"
  | "mail"
  | "rewards"
  | "profile";

type StudioHeaderUtilitiesProps = {
  onAction: (message: string) => void;
};

const panelIds: Record<HeaderPanel, string> = {
  search: "studio-header-search",
  collaboration: "studio-header-collaboration",
  membership: "studio-header-membership",
  notifications: "studio-header-notifications",
  mail: "studio-header-mail",
  rewards: "studio-header-rewards",
  profile: "studio-header-profile",
};

const collaborators = [
  {
    initials: "MS",
    name: "Maya Singh",
    status: "Colour grading Scene 04",
    colour: "#db7547",
    presence: "online",
  },
  {
    initials: "JR",
    name: "Jon Reyes",
    status: "Reviewing storyboard",
    colour: "#3186aa",
    presence: "offline",
  },
  {
    initials: "AK",
    name: "Ari Kim",
    status: "Available to collaborate",
    colour: "#7650d6",
    presence: "online",
  },
] as const;

const onlineCollaboratorCount = collaborators.filter(
  (person) => person.presence === "online",
).length;

export function StudioHeaderUtilities({
  onAction,
}: StudioHeaderUtilitiesProps) {
  const [openPanel, setOpenPanel] = useState<HeaderPanel | null>(null);
  const [searchStatus, setSearchStatus] = useState(
    "Search creators, projects, scenes and assets.",
  );
  const [notificationsUnread, setNotificationsUnread] = useState(true);
  const [mailUnread, setMailUnread] = useState(true);

  const closePanel = (returnFocus = false) => {
    const closingPanel = openPanel;
    setOpenPanel(null);
    if (returnFocus && closingPanel) {
      requestAnimationFrame(() => {
        document
          .querySelector<HTMLButtonElement>(
            `[data-studio-panel-trigger="${closingPanel}"]`,
          )
          ?.focus();
      });
    }
  };

  useEffect(() => {
    if (!openPanel) return;
    const panel = document.getElementById(panelIds[openPanel]);
    const focusTarget = panel?.querySelector<HTMLElement>(
      'input, h2[tabindex="-1"]',
    );
    requestAnimationFrame(() => focusTarget?.focus());

    const handlePointerDown = (event: PointerEvent) => {
      const target = event.target as HTMLElement | null;
      if (
        !target?.closest(
          "[data-studio-panel-trigger], .studio-header-popover",
        )
      ) {
        setOpenPanel(null);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      event.preventDefault();
      const trigger = document.querySelector<HTMLButtonElement>(
        `[data-studio-panel-trigger="${openPanel}"]`,
      );
      setOpenPanel(null);
      requestAnimationFrame(() => trigger?.focus());
    };

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [openPanel]);

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const query =
      new FormData(event.currentTarget).get("query")?.toString().trim() ?? "";
    setSearchStatus(
      query
        ? `Searching Studio for “${query}”.`
        : "Enter a creator, project, scene or asset name.",
    );
  };

  const utilityButton = (
    panel: HeaderPanel,
    label: string,
    title: string,
    icon: ReactNode,
    className = "",
    badge?: ReactNode,
  ) => (
    <Button
      className={`studio-utility-button ${className}`.trim()}
      size="icon"
      aria-label={label}
      aria-controls={panelIds[panel]}
      aria-expanded={openPanel === panel}
      title={title}
      data-studio-panel-trigger={panel}
      onClick={() =>
        setOpenPanel((current) => (current === panel ? null : panel))
      }
    >
      {icon}
      {badge}
    </Button>
  );

  return (
    <>
      <div className="topbar-actions">
        {utilityButton(
          "search",
          "Search",
          "Search",
          <Search aria-hidden="true" />,
        )}
        {utilityButton(
          "collaboration",
          `Collaborate — ${onlineCollaboratorCount} creators online`,
          "Collaborate · Find creators · Build teams",
          <Handshake aria-hidden="true" />,
          "collaboration-utility",
          <span className="collaboration-utility-badge" aria-hidden="true">
            <i />
            {onlineCollaboratorCount}
          </span>,
        )}
        {utilityButton(
          "membership",
          "Membership",
          "Membership · View your plan",
          <Gem aria-hidden="true" />,
          "membership-utility optional-utility",
        )}
        {utilityButton(
          "notifications",
          notificationsUnread ? "Notifications, 31 unread" : "Notifications",
          "Notifications",
          <Bell aria-hidden="true" />,
          "",
          notificationsUnread ? (
            <span className="studio-utility-badge" aria-hidden="true">
              31
            </span>
          ) : undefined,
        )}
        {utilityButton(
          "mail",
          mailUnread ? "Mail, 2 unread" : "Mail",
          "Mail",
          <Mail aria-hidden="true" />,
          "mail-utility optional-utility",
          mailUnread ? (
            <span
              className="studio-utility-badge mail-utility-badge"
              aria-hidden="true"
            >
              2
            </span>
          ) : undefined,
        )}
        {utilityButton(
          "rewards",
          "Achieve Rewards",
          "Achieve Rewards",
          <Trophy aria-hidden="true" />,
          "rewards-utility",
        )}
        {utilityButton(
          "profile",
          "Christopher profile",
          "Christopher · Director",
          <UserRound aria-hidden="true" />,
          "profile-utility",
        )}
      </div>

      {openPanel === "search" && (
        <aside
          className="studio-header-popover"
          id={panelIds.search}
          role="dialog"
          aria-labelledby="studio-search-title"
        >
          <PopoverHeading
            icon={<Search aria-hidden="true" />}
            id="studio-search-title"
            title="Search"
            onClose={() => closePanel(true)}
          />
          <form className="studio-header-search" onSubmit={submitSearch}>
            <label className="visually-hidden" htmlFor="studio-search-query">
              Search Nexkosmo Studio
            </label>
            <input
              id="studio-search-query"
              name="query"
              type="search"
              placeholder="Search creators, projects, scenes or assets…"
            />
            <button type="submit">Search</button>
          </form>
          <p className="studio-popover-status" role="status">
            {searchStatus}
          </p>
        </aside>
      )}

      {openPanel === "collaboration" && (
        <aside
          className="studio-header-popover"
          id={panelIds.collaboration}
          role="dialog"
          aria-labelledby="studio-collaboration-title"
          aria-live="polite"
        >
          <div className="studio-popover-heading">
            <span>
              <UsersRound aria-hidden="true" />
              <h2 id="studio-collaboration-title" tabIndex={-1}>
                Collaboration
              </h2>
            </span>
            <span className="studio-collaboration-summary">
              <i aria-hidden="true" />
              {onlineCollaboratorCount} online
            </span>
            <ClosePopoverButton
              label="Close collaboration panel"
              onClose={() => closePanel(true)}
            />
          </div>
          <div className="studio-collaborator-list">
            {collaborators.map((person) => (
              <div className="studio-collaborator" key={person.name}>
                <span
                  className="studio-popover-avatar"
                  style={{ background: person.colour }}
                >
                  {person.initials}
                </span>
                <span>
                  <strong>{person.name}</strong>
                  <small>{person.status}</small>
                </span>
                <span
                  className={`studio-presence is-${person.presence}`}
                  aria-label={`${person.name} is ${person.presence}`}
                >
                  <i aria-hidden="true" />
                  {person.presence === "online" ? "Online" : "Offline"}
                </span>
                <Button
                  className="studio-popover-icon-button"
                  size="icon"
                  aria-label={`Message ${person.name}`}
                  onClick={() => onAction(`Message ${person.name} opened.`)}
                >
                  <MessageSquare aria-hidden="true" />
                </Button>
              </div>
            ))}
          </div>
          <button
            type="button"
            className="studio-popover-action"
            onClick={() => onAction("Invite collaborator opened.")}
          >
            <UserPlus aria-hidden="true" /> Invite collaborator
          </button>
        </aside>
      )}

      {openPanel === "membership" && (
        <aside
          className="studio-header-popover"
          id={panelIds.membership}
          role="dialog"
          aria-labelledby="studio-membership-title"
        >
          <PopoverHeading
            icon={<Gem aria-hidden="true" />}
            id="studio-membership-title"
            title="Membership"
            onClose={() => closePanel(true)}
          />
          <div className="studio-membership-summary">
            <Gem aria-hidden="true" />
            <span>
              <small>CURRENT PLAN</small>
              <strong>Creator Pro</strong>
              <em>Paid member · Purple tier</em>
            </span>
          </div>
          <button
            type="button"
            className="studio-popover-action"
            onClick={() => onAction("Membership plan and benefits opened.")}
          >
            View plan and benefits
          </button>
        </aside>
      )}

      {openPanel === "notifications" && (
        <aside
          className="studio-header-popover"
          id={panelIds.notifications}
          role="dialog"
          aria-labelledby="studio-notifications-title"
        >
          <PopoverHeading
            icon={<Bell aria-hidden="true" />}
            id="studio-notifications-title"
            title="Notifications"
            onClose={() => closePanel(true)}
          />
          <ul className="studio-header-feed">
            <li>
              <i />
              <span>
                <strong>Render ready</strong>
                <small>Shot 1.5 completed successfully</small>
              </span>
              <time>Now</time>
            </li>
            <li>
              <i className="is-amber" />
              <span>
                <strong>Storyboard review</strong>
                <small>Maya left a production note</small>
              </span>
              <time>8m</time>
            </li>
          </ul>
          <button
            type="button"
            className="studio-popover-action"
            onClick={() => setNotificationsUnread(false)}
          >
            Mark all as read
          </button>
        </aside>
      )}

      {openPanel === "mail" && (
        <aside
          className="studio-header-popover"
          id={panelIds.mail}
          role="dialog"
          aria-labelledby="studio-mail-title"
        >
          <PopoverHeading
            icon={<Mail aria-hidden="true" />}
            id="studio-mail-title"
            title="Mail"
            onClose={() => closePanel(true)}
          />
          <ul className="studio-header-feed">
            <li>
              <span className="studio-feed-avatar">MS</span>
              <span>
                <strong>Maya Singh</strong>
                <small>Colour pass is ready for review.</small>
              </span>
              <time>2m</time>
            </li>
            <li>
              <span className="studio-feed-avatar">JR</span>
              <span>
                <strong>Jon Reyes</strong>
                <small>Updated the Scene 04 storyboard.</small>
              </span>
              <time>15m</time>
            </li>
          </ul>
          <button
            type="button"
            className="studio-popover-action"
            onClick={() => {
              setMailUnread(false);
              onAction("Studio inbox opened.");
            }}
          >
            Open inbox
          </button>
        </aside>
      )}

      {openPanel === "rewards" && (
        <aside
          className="studio-header-popover"
          id={panelIds.rewards}
          role="dialog"
          aria-labelledby="studio-rewards-title"
        >
          <PopoverHeading
            icon={<Trophy aria-hidden="true" />}
            id="studio-rewards-title"
            title="Achieve Rewards™"
            onClose={() => closePanel(true)}
          />
          <div className="studio-reward-stats">
            <span>
              <Star aria-hidden="true" /> Rank 128
            </span>
            <span>
              <Crown aria-hidden="true" /> 146 Creator Hours
            </span>
            <span>
              <Award aria-hidden="true" /> 12 Achievements
            </span>
          </div>
          <div className="studio-reward-card">
            <Gift aria-hidden="true" />
            <span>
              <strong>Ethan Rewards™</strong>
              <small>72% toward the next creator reward</small>
            </span>
          </div>
          <div
            className="studio-reward-progress"
            role="progressbar"
            aria-label="Progress toward the next creator reward"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={72}
          >
            <span />
          </div>
        </aside>
      )}

      {openPanel === "profile" && (
        <aside
          className="studio-header-popover"
          id={panelIds.profile}
          role="dialog"
          aria-labelledby="studio-profile-title"
        >
          <PopoverHeading
            icon={<UserRound aria-hidden="true" />}
            id="studio-profile-title"
            title="Profile"
            onClose={() => closePanel(true)}
          />
          <div className="studio-profile-summary">
            <span className="studio-profile-avatar">C</span>
            <span>
              <strong>Christopher</strong>
              <small>Director · Creator Pro</small>
            </span>
          </div>
          <button
            type="button"
            className="studio-popover-action"
            onClick={() => onAction("Producer management opened.")}
          >
            Manage My Producer
          </button>
          <button
            type="button"
            className="studio-popover-action"
            onClick={() => onAction("Profile and settings opened.")}
          >
            View profile and settings
          </button>
        </aside>
      )}
    </>
  );
}

function PopoverHeading({
  icon,
  id,
  title,
  onClose,
}: {
  icon: ReactNode;
  id: string;
  title: string;
  onClose: () => void;
}) {
  return (
    <div className="studio-popover-heading">
      <span>
        {icon}
        <h2 id={id} tabIndex={-1}>
          {title}
        </h2>
      </span>
      <ClosePopoverButton label={`Close ${title}`} onClose={onClose} />
    </div>
  );
}

function ClosePopoverButton({
  label,
  onClose,
}: {
  label: string;
  onClose: () => void;
}) {
  return (
    <Button
      className="studio-popover-icon-button"
      size="icon"
      aria-label={label}
      onClick={onClose}
    >
      <X aria-hidden="true" />
    </Button>
  );
}
