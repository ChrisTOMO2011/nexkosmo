import type { ReactNode } from "react";
import { Drawer } from "../ui";

type RightSidebarProps = {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
};

export function RightSidebar({
  open,
  title,
  onClose,
  children,
}: RightSidebarProps) {
  return (
    <Drawer
      className="properties-sidebar"
      open={open}
      title={title}
      onClose={onClose}
    >
      {children}
    </Drawer>
  );
}
