"use client";
import { useEffect } from "react";
import Link from "next/link";
export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { console.error(error); }, [error]);
  return (<section className="section"><div className="container" style={{ maxWidth: 560, textAlign: "center" }}><h1 style={{ fontSize: 36 }}>Something went wrong</h1><p className="lead" style={{ margin: "14px auto 26px" }}>This page hit a problem loading. Please try again.</p>
    <div style={{ display: "flex", gap: 12, justifyContent: "center", alignItems: "center" }}><button className="btn btn--primary" onClick={() => reset()}>Try again</button><Link href="/" className="link-arrow">Back to home</Link></div></div></section>);
}
