import Link from "next/link";
import { nav, site } from "@/lib/content";
import Logo from "../brand/Logo";
export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container">
        <div className="footer-grid">
          <div><Logo variant="stacked" tone="dark" height={70} /><p style={{ marginTop: 18, maxWidth: 300, fontSize: 15 }}>{site.tagline}</p></div>
          <div><h4>Explore</h4><ul>{nav.slice(1, 4).map((n) => <li key={n.href}><Link href={n.href}>{n.label}</Link></li>)}</ul></div>
          <div><h4>Learn</h4><ul>{nav.slice(4).map((n) => <li key={n.href}><Link href={n.href}>{n.label}</Link></li>)}</ul></div>
          <div><h4>Talk to us</h4><ul>
            <li><Link href="/book-discovery-call">Book a Discovery Call</Link></li><li><Link href="/contact">Contact</Link></li>
            <li><Link href="/privacy">Privacy</Link></li><li><Link href="/terms">Terms</Link></li></ul></div>
        </div>
        <div className="legal">
          <p>© {new Date().getFullYear()} FORGE. The FORGE platform is in development; product screens use illustrative synthetic data.</p>
          <p>FORGE is an operational monitoring and intelligence layer. It is not an institutional accounting system and does not replace official university financial records. Third-party product names are trademarks of their respective owners; FORGE is not affiliated with or endorsed by them.</p>
        </div>
      </div>
    </footer>
  );
}
