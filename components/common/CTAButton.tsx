"use client";
import { Button } from "antd";
import { useRouter } from "next/navigation";
import type { ComponentProps } from "react";
import { withBase } from "@/lib/path";
import { track, type GosEvent } from "@/lib/analytics";

type Props = Omit<ComponentProps<typeof Button>, "href"> & {
  href: string;
  tone?: "primary" | "secondary" | "ghost-light";
  event?: GosEvent;
};

/** Renders a real anchor (accessible, crawlable) but navigates client-side. */
export default function CTAButton({ href, tone = "primary", event, children, onClick, style, ...rest }: Props) {
  const router = useRouter();
  const external = /^(https?:|mailto:)/.test(href);
  const styles: Record<string, React.CSSProperties> = {
    primary: {},
    secondary: { background: "#fff", borderColor: "#174A82", color: "#174A82" },
    "ghost-light": { background: "transparent", borderColor: "#fff", color: "#fff" },
  };
  return (
    <Button
      size="large"
      href={external ? href : withBase(href)}
      {...rest}
      className={`${tone === "primary" ? "btn-shine" : tone === "ghost-light" ? "btn-glass" : ""} ${rest.className ?? ""}`}
      style={{ ...styles[tone], ...style }}
      onClick={(e) => {
        if (event) track(event, { href });
        onClick?.(e);
        if (!external && !e.metaKey && !e.ctrlKey && !e.shiftKey) {
          e.preventDefault();
          router.push(href);
        }
      }}
    >
      {children}
    </Button>
  );
}
