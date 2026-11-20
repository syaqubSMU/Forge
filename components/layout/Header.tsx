"use client";
import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button, Drawer } from "antd";
import { MenuOutlined } from "@ant-design/icons";
import { withBase } from "@/lib/path";
import { nav } from "@/lib/content";
import CTAButton from "../common/CTAButton";

export default function Header() {
  const path = usePathname();
  const [open, setOpen] = useState(false);
  const isActive = (href: string) => (href === "/" ? path === "/" : path.startsWith(href));
  return (
    <header className="site-header">
      <div className="container inner">
        <Link href="/" className="brand" aria-label="Forge — home">
          <Image src={withBase("/logo.webp")} alt="" width={130} height={68} priority style={{ height: 68, width: "auto" }} />
          <span className="wordmark">Forge<i aria-hidden="true">.</i></span>
        </Link>
        <nav className="desktop-nav" aria-label="Primary">
          {nav.map((n) => (
            <Link key={n.href} href={n.href} className="navlink" aria-current={isActive(n.href) ? "page" : undefined}>{n.label}</Link>
          ))}
        </nav>
        <span className="header-cta">
          <CTAButton href="/book-consultation" event="consultation_cta_clicked">Book a Consultation</CTAButton>
        </span>
        <Button className="mobile-only" size="large" icon={<MenuOutlined />} aria-label="Open menu" onClick={() => setOpen(true)} />
      </div>
      <Drawer title="Menu" placement="right" open={open} onClose={() => setOpen(false)} width={300}>
        <nav aria-label="Mobile" style={{ display: "grid", gap: 4 }}>
          {nav.map((n) => (
            <Link key={n.href} href={n.href} onClick={() => setOpen(false)} aria-current={isActive(n.href) ? "page" : undefined}
              style={{ padding: "12px 8px", fontSize: 17, textDecoration: "none", fontWeight: isActive(n.href) ? 700 : 500 }}>{n.label}</Link>
          ))}
        </nav>
        <div style={{ marginTop: 20 }}><CTAButton href="/book-consultation" event="consultation_cta_clicked" block>Book a Consultation</CTAButton></div>
      </Drawer>
    </header>
  );
}
