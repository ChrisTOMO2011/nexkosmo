import { X } from "lucide-react";
import type { ReactNode } from "react";
import { Button } from "./Button";

type DrawerProps = {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
  className?: string;
  showClose?: boolean;
};

export function Drawer({
  open,
  title,
  onClose,
  children,
  className = "",
  showClose = true,
}: DrawerProps) {
  return (
    <aside
      className={`ui-drawer ${open ? "is-open" : ""} ${className}`.trim()}
      aria-label={title}
    >
      {showClose && (
        <Button
          className="properties-close"
          size="icon"
          aria-label={`Close ${title}`}
          onClick={onClose}
        >
          <X aria-hidden="true" />
        </Button>
      )}
      {children}
    </aside>
  );
}
