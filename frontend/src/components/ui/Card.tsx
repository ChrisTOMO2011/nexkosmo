import type { HTMLAttributes } from "react";

export function Card({
  className = "",
  children,
  ...props
}: HTMLAttributes<HTMLElement>) {
  return (
    <article className={`ui-card ${className}`.trim()} {...props}>
      {children}
    </article>
  );
}
