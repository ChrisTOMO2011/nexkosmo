import type { ReactNode } from "react";
import { Button } from "../../../../components/ui";
import type { DomainAssetStatus } from "./domain-workspace.types";

export type ActionCardPresentation = Readonly<{
  id: string;
  label: string;
  description: string;
  icon: ReactNode;
  status?: DomainAssetStatus;
}>;

type ActionCardsProps<T extends ActionCardPresentation> = {
  actions: readonly T[];
  className: string;
  onActivate: (action: T) => void;
};

export function ActionCards<T extends ActionCardPresentation>({
  actions,
  className,
  onActivate,
}: ActionCardsProps<T>) {
  return (
    <div className={className}>
      {actions.map((action) => (
        <Button
          key={action.id}
          data-status={action.status ?? "available"}
          onClick={() => onActivate(action)}
        >
          {action.icon}
          <span>
            <strong>{action.label}</strong>
            <small>{action.description}</small>
          </span>
        </Button>
      ))}
    </div>
  );
}
