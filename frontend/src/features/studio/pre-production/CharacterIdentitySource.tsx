import { Check, CloudUpload, Info, Sparkles } from "lucide-react";
import { useRef, useState, type DragEvent } from "react";

type CharacterIdentitySourceProps = {
  selectedFace: number;
  onSelectFace: (index: number) => void;
  onPlaceholder: (message: string) => void;
};

export function CharacterIdentitySource({
  selectedFace,
  onSelectFace,
  onPlaceholder,
}: CharacterIdentitySourceProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);

  function handleFile(file?: File) {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      onPlaceholder("Please choose a JPG or PNG image.");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      setUploadedImage(String(reader.result));
      onPlaceholder(`${file.name} added as the identity source.`);
    };
    reader.readAsDataURL(file);
  }

  function handleDrop(event: DragEvent<HTMLButtonElement>) {
    event.preventDefault();
    handleFile(event.dataTransfer.files[0]);
  }

  return (
    <section className="identity-source-panel" aria-labelledby="identity-source-title">
      <div className="character-heading">
        <p className="breadcrumb">
          CHARACTERS <span>›</span> CHRISTOPHER
        </p>
        <h1>
          Christopher
          <button type="button" aria-label="Edit Christopher name">
            <span aria-hidden="true">⌕</span>
          </button>
        </h1>
        <p className="character-role">Lead Character</p>
        <div className="identity-tags">
          <span>Actor</span>
          <span>Human Male</span>
        </div>
      </div>

      <h2 id="identity-source-title">
        IDENTITY SOURCE
        <Info aria-hidden="true" />
      </h2>

      <button
        className="upload-dropzone"
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        {uploadedImage ? (
          <img src={uploadedImage} alt="Uploaded identity source" />
        ) : (
          <>
            <CloudUpload aria-hidden="true" />
            <strong>Drag &amp; drop face image here</strong>
            <span>or click to upload</span>
            <small>JPG, PNG up to 10MB</small>
          </>
        )}
      </button>
      <input
        ref={inputRef}
        className="visually-hidden"
        type="file"
        accept=".jpg,.jpeg,.png,image/jpeg,image/png"
        aria-label="Upload face image"
        onChange={(event) => handleFile(event.target.files?.[0])}
      />

      <div className="face-thumbnails" aria-label="Identity face variants">
        {[0, 1, 2, 3].map((index) => (
          <button
            className={`face-thumb face-${index + 1} ${selectedFace === index ? "is-selected" : ""}`}
            type="button"
            key={index}
            aria-label={`Select face variant ${index + 1}`}
            aria-pressed={selectedFace === index}
            onClick={() => onSelectFace(index)}
          >
            {selectedFace === index && (
              <span className="selection-check">
                <Check aria-hidden="true" />
              </span>
            )}
          </button>
        ))}
      </div>

      <button
        className="generate-button"
        type="button"
        onClick={() => onPlaceholder("AI face generation is a placeholder.")}
      >
        <Sparkles aria-hidden="true" />
        Generate with AI
      </button>
    </section>
  );
}
