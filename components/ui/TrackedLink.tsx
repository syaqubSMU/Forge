"use client";
import Link from "next/link";
import type { ReactNode } from "react";
import { track, type GosEvent } from "@/lib/analytics";
export default function TrackedLink({ href, className, event, children }: { href: string; className?: string; event: GosEvent; children: ReactNode }) {
  return <Link href={href} className={className} onClick={() => track(event, { href })}>{children}</Link>;
}
