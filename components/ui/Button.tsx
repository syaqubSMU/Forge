import Link from "next/link";
import type { ReactNode } from "react";
import TrackedLink from "./TrackedLink";
import type { GosEvent } from "@/lib/analytics";

type Props = { href: string; children: ReactNode; variant?: "primary" | "secondary" | "accent" | "ghost-light"; event?: GosEvent; size?: "md" | "lg"; className?: string };

/** Consistent button geometry across the site. Real anchors (crawlable, accessible). */
export default function Button({ href, children, variant = "primary", event, size = "md", className = "" }: Props) {
  const cls = `btn btn--${variant} btn--${size} ${className}`;
  return event ? <TrackedLink href={href} className={cls} event={event}>{children}</TrackedLink> : <Link href={href} className={cls}>{children}</Link>;
}
