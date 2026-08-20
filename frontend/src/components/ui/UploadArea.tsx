import { CloudUpload } from "lucide-react";
import { useRef, type DragEvent, type ReactNode } from "react";

type UploadAreaProps = {
  label: string;
  helperText?: string;
  accept?: string;
  onFile: (file: File) => void;
  onActivate?: () => boolean | void;
  preview?: ReactNode;
  className?: string;
};

export function UploadArea({
  label,
  helperText,
  accept,
  onFile,
  onActivate,
  preview,
  className = "",
}: UploadAreaProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  function selectFile(file?: File) {
    if (file) onFile(file);
  }

  function handleDrop(event: DragEvent<HTMLButtonElement>) {
    event.preventDefault();
    if (onActivate?.() === false) return;
    selectFile(event.dataTransfer.files[0]);
  }

  function handleActivate() {
    if (onActivate?.() === false) return;
    inputRef.current?.click();
  }

  return (
    <>
      <button
        className={`ui-upload-area ${className}`.trim()}
        type="button"
        onClick={handleActivate}
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        {preview ?? (
          <>
            <CloudUpload aria-hidden="true" />
            <strong>{label}</strong>
            {helperText && <small>{helperText}</small>}
          </>
        )}
      </button>
      <input
        ref={inputRef}
        className="visually-hidden"
        type="file"
        accept={accept}
        aria-label={label}
        onChange={(event) => selectFile(event.target.files?.[0])}
      />
    </>
  );
}
