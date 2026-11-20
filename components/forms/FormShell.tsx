import type { ReactNode } from "react";
export default function FormShell({ children }: { children: ReactNode }) {
  return <div className="gcard" style={{ maxWidth: 680, position: "relative" }}>{children}</div>;
}
