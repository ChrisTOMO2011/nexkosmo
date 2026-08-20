import {
  Bell,
  Brain,
  Coins,
  MessageSquare,
  Search,
  UserRound,
  UsersRound,
} from "lucide-react";
import type { ReactNode } from "react";
import type { WorkflowStage } from "../../app/workflow";
import { CanonicalLogo } from "../brand/CanonicalLogo";
import { Button } from "../ui";
import { WorkflowNavigation } from "./WorkflowNavigation";

type TopNavigationProps = {
  activeStage: WorkflowStage;
  projectId: string;
};

const utilities: readonly [string, ReactNode][] = [
  ["Search unavailable", <Search aria-hidden="true" />],
  ["Brain status not connected", <Brain aria-hidden="true" />],
  ["Credits unavailable", <Coins aria-hidden="true" />],
  ["Collaboration unavailable", <UsersRound aria-hidden="true" />],
  ["Alerts unavailable", <Bell aria-hidden="true" />],
  ["Messages unavailable", <MessageSquare aria-hidden="true" />],
  ["Profile unavailable", <UserRound aria-hidden="true" />],
];

export function TopNavigation({ activeStage, projectId }: TopNavigationProps) {
  return (
    <header className="top-navigation">
      <CanonicalLogo />
      <WorkflowNavigation activeStage={activeStage} projectId={projectId} />
      <div className="top-navigation__context" aria-label="Project context">
        <span>Project</span>
        <strong>{projectId}</strong>
      </div>
      <div className="top-navigation__utilities" aria-label="Global tools">
        {utilities.map(([label, icon]) => (
          <Button
            className="utility-button"
            key={label}
            aria-label={label}
            title={label}
            disabled
          >
            {icon}
          </Button>
        ))}
      </div>
    </header>
  );
}

