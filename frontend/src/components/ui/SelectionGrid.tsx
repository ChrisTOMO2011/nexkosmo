import type { HTMLAttributes } from "react";

export function SelectionGrid({
  className = "",
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`ui-selection-grid ${className}`.trim()} {...props}>
      {children}
    </div>
  );
}
