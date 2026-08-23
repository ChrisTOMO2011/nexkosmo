import { ChevronDown } from "lucide-react";
import type { SelectHTMLAttributes } from "react";

export type DropdownOption = {
  label: string;
  value: string;
  disabled?: boolean;
};

type DropdownProps = Omit<
  SelectHTMLAttributes<HTMLSelectElement>,
  "children"
> & {
  label: string;
  options: readonly DropdownOption[];
};

export function Dropdown({
  label,
  options,
  className = "",
  ...props
}: DropdownProps) {
  return (
    <span className={`ui-dropdown ${className}`.trim()}>
      <select aria-label={label} {...props}>
        {options.map((option) => (
          <option
            value={option.value}
            disabled={option.disabled}
            key={option.value}
          >
            {option.label}
          </option>
        ))}
      </select>
      <ChevronDown aria-hidden="true" />
    </span>
  );
}
