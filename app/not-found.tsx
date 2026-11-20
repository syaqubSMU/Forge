import Section from "@/components/ui/Section";
import Button from "@/components/ui/Button";
export default function NotFound() {
  return (<Section tone="white"><div style={{ maxWidth: 560, margin: "0 auto", textAlign: "center" }}><h1 style={{ fontSize: 40 }}>Page not found</h1><p className="lead" style={{ margin: "14px auto 26px" }}>That page doesn&apos;t exist or has moved.</p><Button href="/">Back to home</Button></div></Section>);
}
