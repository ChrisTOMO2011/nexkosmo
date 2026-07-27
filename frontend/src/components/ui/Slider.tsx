import type { CSSProperties } from "react";

type SliderProps = {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (value: number) => void;
  formatValue?: (value: number) => string;
  showValue?: boolean;
  className?: string;
};

export function Slider({
  label,
  value,
  min,
  max,
  step = 1,
  onChange,
  formatValue = String,
  showValue = true,
  className = "",
}: SliderProps) {
  const progress = ((value - min) / (max - min)) * 100;
  const sliderStyle = {
    "--range-progress": `${progress}%`,
  } as CSSProperties;

  return (
    <label className={`ui-slider slider-field ${className}`.trim()}>
      <span>
        {label} {showValue && <output>{formatValue(value)}</output>}
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        style={sliderStyle}
        aria-label={label}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}
