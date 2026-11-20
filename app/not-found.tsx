import Link from "next/link";
export default function NotFound() {
  return (
    <section className="section"><div className="container" style={{ maxWidth: 640, textAlign: "center" }}>
      <h1 style={{ fontSize: 32 }}>Page not found.</h1>
      <p className="lead" style={{ margin: "12px auto 24px" }}>That page doesn’t exist or has moved.</p>
      <Link href="/" style={{ fontWeight: 600 }}>Back to home</Link>
    </div></section>
  );
}
