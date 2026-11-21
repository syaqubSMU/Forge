import Link from "next/link";
import { nav, site } from "@/lib/content";
import Logo from "../brand/Logo";
export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container">
        <div className="footer-grid footer-grid--simple">
          <div><Logo variant="stacked" tone="dark" height={70} /><p style={{ marginTop: 18, maxWidth: 300, fontSize: 15 }}>{site.tagline}</p></div>
          <div><h4>Explore</h4><ul>{nav.map((n) => <li key={n.href}><Link href={n.href}>{n.label}</Link></li>)}<li><Link href="/products/travel-budget-calculator">Free Travel Budget Calculator</Link></li></ul></div>
        </div>
        <div className="legal">
          <p>© {new Date().getFullYear()} FORGE. The FORGE platform is in development; product screens use illustrative synthetic data.</p>
          <p>FORGE tools support departmental monitoring. FORGE is an operational monitoring and intelligence layer, not an institutional accounting system, and does not replace official university financial records. Third-party product names are trademarks of their respective owners; FORGE is not affiliated with or endorsed by them.</p>
        </div>
      </div>
    </footer>
  );
}
