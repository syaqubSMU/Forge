import CTAButton from "../common/CTAButton";
export default function FreeTool() {
  return (
    <section style={{ background: "#fff", borderBottom: "1px solid var(--border)" }}>
      <div className="container" style={{ display: "flex", flexWrap: "wrap", gap: 20, alignItems: "center", justifyContent: "space-between", padding: "28px 20px" }}>
        <div style={{ maxWidth: 720 }}>
          <div className="eyebrow" style={{ marginBottom: 6 }}>Free tool</div>
          <h2 style={{ fontSize: 24 }}>Try the Forge Travel Calculator.</h2>
          <p style={{ margin: "6px 0 0", color: "var(--muted)" }}>A free interactive tool to help estimate travel costs. No sign-up required.</p>
        </div>
        <CTAButton href="/resources/travel-calculator">Use the Free Travel Calculator →</CTAButton>
      </div>
    </section>
  );
}
