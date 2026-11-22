"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Drawer } from "antd";
import { MenuOutlined } from "@ant-design/icons";
import { nav } from "@/lib/content";
import { withBase } from "@/lib/path";
import Logo from "../brand/Logo";
import Button from "../ui/Button";

export default function Header() {
  const path = usePathname() || "/";
  const [open, setOpen] = useState(false);
  const isActive = (href: string) => (href === "/" ? path === "/" : path.startsWith(href));
  return (
    <header className="site-header">
      <div className="container inner">
        <Link href="/" className="brand" aria-label="FORGE — home"><Logo variant="horizontal" height={34} /></Link>
        <nav className="desktop-nav" aria-label="Primary">
          {nav.map((n) => (<Link key={n.href} href={n.href} className="navlink" aria-current={isActive(n.href) ? "page" : undefined}>{n.label}</Link>))}
          <a href={withBase("/signal/")} className="navlink">Forge Signal</a>
        </nav>
        <span className="header-cta"><Button href="/products/#request">Request a Demo</Button></span>
        <button className="menu-btn" aria-label="Open menu" aria-expanded={open} onClick={() => setOpen(true)}><MenuOutlined /></button>
      </div>
      <Drawer title={<Logo variant="horizontal" height={26} />} placement="right" open={open} onClose={() => setOpen(false)} width={320}>
        <nav aria-label="Mobile" style={{ display: "grid", gap: 2 }}>
          {nav.map((n) => (
            <Link key={n.href} href={n.href} onClick={() => setOpen(false)} aria-current={isActive(n.href) ? "page" : undefined}
              style={{ padding: "13px 6px", fontSize: 17, textDecoration: "none", fontWeight: isActive(n.href) ? 700 : 500, borderBottom: "1px solid var(--border)" }}>{n.label}</Link>
          ))}
          <a href={withBase("/signal/")} onClick={() => setOpen(false)} style={{ padding: "13px 6px", fontSize: 17, textDecoration: "none", fontWeight: 500, borderBottom: "1px solid var(--border)" }}>Forge Signal</a>
        </nav>
        <div style={{ marginTop: 24 }}><Button href="/products/#request" className="btn--block">Request a Demo</Button></div>
      </Drawer>
    </header>
  );
}
