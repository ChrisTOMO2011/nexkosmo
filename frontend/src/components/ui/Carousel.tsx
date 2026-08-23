import type { ReactNode } from "react";

type CarouselProps<T> = {
  items: readonly T[];
  activeIndex: number;
  onChange: (index: number) => void;
  renderItem: (item: T, index: number) => ReactNode;
  label: string;
  className?: string;
};

export function Carousel<T>({
  items,
  activeIndex,
  onChange,
  renderItem,
  label,
  className = "",
}: CarouselProps<T>) {
  return (
    <div
      className={`ui-carousel ${className}`.trim()}
      role="region"
      aria-roledescription="carousel"
      aria-label={label}
    >
      <div className="ui-carousel__viewport">
        {renderItem(items[activeIndex], activeIndex)}
      </div>
      <div className="carousel-dots" aria-label={`${label} pagination`}>
        {items.map((_, index) => (
          <button
            type="button"
            key={index}
            className={activeIndex === index ? "is-active" : ""}
            aria-label={`Show item ${index + 1}`}
            aria-pressed={activeIndex === index}
            onClick={() => onChange(index)}
          />
        ))}
      </div>
    </div>
  );
}
