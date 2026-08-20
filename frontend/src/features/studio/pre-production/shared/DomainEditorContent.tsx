import type { ReactNode } from "react";

type DomainEditorContentProps = {
  children: ReactNode;
};

export function DomainEditorContent({ children }: DomainEditorContentProps) {
  return <div className="editor-scroll">{children}</div>;
}
