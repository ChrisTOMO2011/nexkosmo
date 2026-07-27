import type { HTMLAttributes } from "react";

export function AssetGrid({
  className = "",
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`ui-asset-grid ${className}`.trim()} {...props}>
      {children}
    </div>
  );
}
