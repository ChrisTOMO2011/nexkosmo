import { ChevronLeft, ChevronRight, Expand } from "lucide-react";
import type { ReactNode } from "react";
import { Carousel } from "../../../../components/ui";

export type DomainPreviewMode = {
  id: string;
  label: string;
  icon: ReactNode;
  onSelect: () => void;
};

type DomainPreviewCarouselProps<T> = {
  items: readonly T[];
  activeIndex: number;
  label: string;
  modes: readonly DomainPreviewMode[];
  onChange: (index: number) => void;
  onPrevious: () => void;
  onNext: () => void;
  onExpand: () => void;
  getPreviewClassName: (item: T, index: number) => string;
  renderPreviewContent?: (item: T, index: number) => ReactNode;
  sectionClassName?: string;
  carouselClassName?: string;
  expandLabel?: string;
};

export function DomainPreviewCarousel<T>({
  items,
  activeIndex,
  label,
  modes,
  onChange,
  onPrevious,
  onNext,
  onExpand,
  getPreviewClassName,
  renderPreviewContent,
  sectionClassName = "character-preview",
  carouselClassName = "character-preview-carousel",
  expandLabel = "Open fullscreen preview",
}: DomainPreviewCarouselProps<T>) {
  return (
    <section className={sectionClassName} aria-label={label}>
      <Carousel
        className={carouselClassName}
        items={items}
        activeIndex={activeIndex}
        onChange={onChange}
        label={label}
        renderItem={(item, index) => (
          <div className={getPreviewClassName(item, index)}>
            {renderPreviewContent?.(item, index)}
            <div className="preview-controls">
              {modes.map((mode) => (
                <button type="button" key={mode.id} onClick={mode.onSelect}>
                  {mode.icon}
                  {mode.label}
                </button>
              ))}
              <button
                className="preview-expand"
                type="button"
                aria-label={expandLabel}
                onClick={onExpand}
              >
                <Expand aria-hidden="true" />
              </button>
            </div>
            <button
              className="preview-arrow preview-arrow-left"
              type="button"
              aria-label="Previous preview"
              onClick={onPrevious}
            >
              <ChevronLeft aria-hidden="true" />
            </button>
            <button
              className="preview-arrow preview-arrow-right"
              type="button"
              aria-label="Next preview"
              onClick={onNext}
            >
              <ChevronRight aria-hidden="true" />
            </button>
          </div>
        )}
      />
    </section>
  );
}
