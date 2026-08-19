import type { ReactNode } from "react";

type PropertyFieldProps = {
  label: string;
  children: ReactNode;
  hint?: string;
  className?: string;
};

export function PropertyField({
  label,
  children,
  hint,
  className = "",
}: PropertyFieldProps) {
  return (
    <label className={`ui-property-field ${className}`.trim()}>
      <span>{label}</span>
      {children}
      {hint && <small>{hint}</small>}
    </label>
  );
}
