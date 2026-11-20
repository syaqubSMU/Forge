"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Drawer } from "antd";
import { MenuOutlined } from "@ant-design/icons";
import { nav } from "@/lib/content";
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
        </nav>
        <span className="header-cta"><Button href="/book-discovery-call" event="consultation_cta_clicked">Book a Discovery Call</Button></span>
        <button className="menu-btn" aria-label="Open menu" aria-expanded={open} onClick={() => setOpen(true)}><MenuOutlined /></button>
      </div>
      <Drawer title={<Logo variant="horizontal" height={28} />} placement="right" open={open} onClose={() => setOpen(false)} width={320}>
        <nav aria-label="Mobile" style={{ display: "grid", gap: 2 }}>
          {nav.map((n) => (
            <Link key={n.href} href={n.href} onClick={() => setOpen(false)} aria-current={isActive(n.href) ? "page" : undefined}
              style={{ padding: "13px 6px", fontSize: 17, textDecoration: "none", fontWeight: isActive(n.href) ? 700 : 500, borderBottom: "1px solid var(--border)" }}>{n.label}</Link>
          ))}
        </nav>
        <div style={{ marginTop: 24 }}><Button href="/book-discovery-call" event="consultation_cta_clicked" className="btn--block">Book a Discovery Call</Button></div>
      </Drawer>
    </header>
  );
}
