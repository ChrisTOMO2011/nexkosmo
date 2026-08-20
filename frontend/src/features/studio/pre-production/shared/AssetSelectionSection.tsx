import type { ReactNode } from "react";

type AssetSelectionSectionProps = {
  title: string;
  titleId: string;
  className?: string;
  children: ReactNode;
};

export function AssetSelectionSection({
  title,
  titleId,
  className = "",
  children,
}: AssetSelectionSectionProps) {
  return (
    <section
      className={`selector-section ${className}`.trim()}
      aria-labelledby={titleId}
    >
      <h3 id={titleId}>{title}</h3>
      {children}
    </section>
  );
}
