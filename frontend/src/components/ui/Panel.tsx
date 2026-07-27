import type { HTMLAttributes, ReactNode } from "react";

export type PanelProps = HTMLAttributes<HTMLElement> & {
  title?: string;
  description?: string;
  actions?: ReactNode;
};

export function Panel({
  title,
  description,
  actions,
  className = "",
  children,
  ...props
}: PanelProps) {
  return (
    <section className={`ui-panel ${className}`.trim()} {...props}>
      {(title || description || actions) && (
        <header className="ui-panel__header">
          <div>
            {title && <h2>{title}</h2>}
            {description && <p>{description}</p>}
          </div>
          {actions && <div className="ui-panel__actions">{actions}</div>}
        </header>
      )}
      <div className="ui-panel__body">{children}</div>
    </section>
  );
}
