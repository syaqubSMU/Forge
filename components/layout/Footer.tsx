import Link from "next/link";
import { site, services } from "@/lib/content";
export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container">
        <div className="footer-grid">
          <div>
            <strong className="wordmark wordmark--footer">{site.name}<i aria-hidden="true">.</i></strong>
            <p style={{ marginTop: 10 }}>{site.tagline}</p>
          </div>
          <div><h4>Solutions</h4><ul>{services.map((s) => <li key={s.slug}><Link href={`/solutions/${s.slug}`}>{s.title}</Link></li>)}</ul></div>
          <div><h4>Explore</h4><ul>
            <li><Link href="/products">Products</Link></li><li><Link href="/ai-automation">AI & Automation</Link></li>
            <li><Link href="/resources">Resources</Link></li><li><Link href="/about">About</Link></li></ul></div>
          <div><h4>Company</h4><ul>
            <li><Link href="/contact">Contact</Link></li><li><Link href="/book-consultation">Book a Consultation</Link></li>
            <li><Link href="/privacy">Privacy</Link></li><li><Link href="/terms">Terms</Link></li></ul></div>
        </div>
        <div className="legal">
          © {new Date().getFullYear()} Forge. Prices shown are indicative. Forge provides operational tools and consulting; it does not provide legal advice or guarantee compliance, audit outcomes, or funder approval.
        </div>
      </div>
    </footer>
  );
}
