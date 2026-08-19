import {
  Box,
  ChevronLeft,
  ChevronRight,
  Expand,
  Hexagon,
} from "lucide-react";
import { Carousel } from "../../../components/ui";

type CharacterPreviewProps = {
  slide: number;
  onSlideChange: (slide: number) => void;
  onPlaceholder: (message: string) => void;
};

export function CharacterPreview({
  slide,
  onSlideChange,
  onPlaceholder,
}: CharacterPreviewProps) {
  const previous = () => onSlideChange((slide + 4) % 5);
  const next = () => onSlideChange((slide + 1) % 5);

  return (
    <section className="character-preview" aria-label="Character cinematic preview">
      <Carousel
        className="character-preview-carousel"
        items={[0, 1, 2, 3, 4]}
        activeIndex={slide}
        onChange={onSlideChange}
        label="Character cinematic preview"
        renderItem={(_, activeIndex) => (
          <div className={`preview-image preview-slide-${activeIndex}`}>
            <div className="preview-shade" />
            <div className="preview-controls">
              <button
                type="button"
                onClick={() => onPlaceholder("Lit viewport mode selected.")}
              >
                <Hexagon aria-hidden="true" />
                Lit
              </button>
              <button
                type="button"
                onClick={() => onPlaceholder("Wireframe viewport mode selected.")}
              >
                <Box aria-hidden="true" />
                Wireframe
              </button>
              <button
                className="preview-expand"
                type="button"
                aria-label="Open fullscreen preview"
                onClick={() =>
                  onPlaceholder("Fullscreen preview placeholder opened.")
                }
              >
                <Expand aria-hidden="true" />
              </button>
            </div>
            <button
              className="preview-arrow preview-arrow-left"
              type="button"
              aria-label="Previous preview"
              onClick={previous}
            >
              <ChevronLeft aria-hidden="true" />
            </button>
            <button
              className="preview-arrow preview-arrow-right"
              type="button"
              aria-label="Next preview"
              onClick={next}
            >
              <ChevronRight aria-hidden="true" />
            </button>
          </div>
        )}
      />
    </section>
  );
}
