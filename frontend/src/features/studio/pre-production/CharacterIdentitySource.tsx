import { Check, CloudUpload, Info, Pencil, Sparkles } from "lucide-react";
import { useState } from "react";
import { Button, UploadArea } from "../../../components/ui";

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

  return (
    <section className="identity-source-panel" aria-labelledby="identity-source-title">
      <div className="character-heading">
        <p className="breadcrumb">
          CHARACTERS <span>›</span> CHRISTOPHER
        </p>
        <h1>
          Christopher
          <button type="button" aria-label="Edit Christopher name">
            <Pencil aria-hidden="true" />
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

      <UploadArea
        className="upload-dropzone"
        label="Upload face image"
        helperText="JPG, PNG up to 10MB"
        accept=".jpg,.jpeg,.png,image/jpeg,image/png"
        onFile={handleFile}
        preview={uploadedImage ? (
          <img src={uploadedImage} alt="Uploaded identity source" />
        ) : (
          <>
            <CloudUpload aria-hidden="true" />
            <strong>Drag &amp; drop face image here</strong>
            <span>or click to upload</span>
            <small>JPG, PNG up to 10MB</small>
          </>
        )}
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

      <Button
        className="generate-button"
        leadingIcon={<Sparkles aria-hidden="true" />}
        onClick={() => onPlaceholder("AI face generation is a placeholder.")}
      >
        Generate with AI
      </Button>
    </section>
  );
}
