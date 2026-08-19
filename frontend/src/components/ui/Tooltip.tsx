import { useId, type ReactNode } from "react";

type TooltipProps = {
  content: string;
  children: ReactNode;
};

export function Tooltip({ content, children }: TooltipProps) {
  const id = useId();

  return (
    <span className="ui-tooltip" aria-describedby={id}>
      {children}
      <span className="ui-tooltip__content" id={id} role="tooltip">
        {content}
      </span>
    </span>
  );
}
