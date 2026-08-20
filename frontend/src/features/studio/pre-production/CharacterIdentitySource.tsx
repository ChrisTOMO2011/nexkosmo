import { CloudUpload, Info, Pencil, Sparkles } from "lucide-react";
import { Button, UploadArea } from "../../../components/ui";
import { DomainSourcePanel, type DeferredActionId } from "./shared";

type CharacterIdentitySourceProps = {
  displayName: string;
  role: string;
  identityType: string;
  selectedFace: number;
  onSelectFace: (index: number) => void;
  onDeferredAction: (action: DeferredActionId) => void;
};

export function CharacterIdentitySource({
  displayName,
  role,
  identityType,
  selectedFace,
  onSelectFace,
  onDeferredAction,
}: CharacterIdentitySourceProps) {
  return (
    <DomainSourcePanel
      title="IDENTITY SOURCE"
      titleId="identity-source-title"
      titleAdornment={<Info aria-hidden="true" />}
      heading={
        <div className="character-heading">
          <p className="breadcrumb">
            CHARACTERS <span>›</span> {displayName.toUpperCase()}
          </p>
          <h1>
            {displayName}
            <button type="button" aria-label={`Edit ${displayName} name`}>
              <Pencil aria-hidden="true" />
            </button>
          </h1>
          <p className="character-role">{role} Character</p>
          <div className="identity-tags">
            <span>Actor</span>
            <span>{identityType}</span>
          </div>
        </div>
      }
      source={
        <UploadArea
          className="upload-dropzone"
          label="Upload face image"
          helperText="JPG, PNG up to 10MB"
          accept=".jpg,.jpeg,.png,image/jpeg,image/png"
          onActivate={() => {
            onDeferredAction("asset-upload");
            return false;
          }}
          onFile={() => onDeferredAction("asset-upload")}
          preview={
            <>
              <CloudUpload aria-hidden="true" />
              <strong>Drag &amp; drop face image here</strong>
              <span>or click to upload</span>
              <small>JPG, PNG up to 10MB</small>
            </>
          }
        />
      }
      variants={
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
            </button>
          ))}
        </div>
      }
      primaryAction={
        <Button
          className="generate-button"
          leadingIcon={<Sparkles aria-hidden="true" />}
          onClick={() => onDeferredAction("character-generation")}
        >
          Generate with AI
        </Button>
      }
    />
  );
}
