import { Box, Hexagon } from "lucide-react";
import { DomainPreviewCarousel } from "./shared";

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
    <DomainPreviewCarousel
      items={[0, 1, 2, 3, 4]}
      activeIndex={slide}
      label="Character cinematic preview"
      modes={[
        {
          id: "lit",
          label: "Lit",
          icon: <Hexagon aria-hidden="true" />,
          onSelect: () => onPlaceholder("Lit viewport mode selected."),
        },
        {
          id: "wireframe",
          label: "Wireframe",
          icon: <Box aria-hidden="true" />,
          onSelect: () => onPlaceholder("Wireframe viewport mode selected."),
        },
      ]}
      onChange={onSlideChange}
      onPrevious={previous}
      onNext={next}
      onExpand={() =>
        onPlaceholder("Fullscreen preview placeholder opened.")
      }
      getPreviewClassName={(_, activeIndex) =>
        `preview-image preview-slide-${activeIndex}`
      }
      renderPreviewContent={() => <div className="preview-shade" />}
    />
  );
}
