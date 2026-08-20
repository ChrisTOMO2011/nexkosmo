import type { ReactNode } from "react";

type DomainSourcePanelProps = {
  title: string;
  titleId: string;
  heading: ReactNode;
  source: ReactNode;
  variants: ReactNode;
  primaryAction: ReactNode;
  titleAdornment?: ReactNode;
  className?: string;
};

export function DomainSourcePanel({
  title,
  titleId,
  heading,
  source,
  variants,
  primaryAction,
  titleAdornment,
  className = "identity-source-panel",
}: DomainSourcePanelProps) {
  return (
    <section className={className} aria-labelledby={titleId}>
      {heading}
      <h2 id={titleId}>
        {title}
        {titleAdornment}
      </h2>
      {source}
      {variants}
      {primaryAction}
    </section>
  );
}
