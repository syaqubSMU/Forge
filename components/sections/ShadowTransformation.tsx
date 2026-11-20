const Chain = ({ items, cls }: { items: string[]; cls: string }) => (
  <div className={`chain ${cls}`}>{items.map((x, i) => (<span key={x} style={{ display: "contents" }}><span className="chip">{x}</span>{i < items.length - 1 && <span className="arr" aria-hidden="true">→</span>}</span>))}</div>
);
export default function ShadowTransformation() {
  return (
    <div className="shadow-vs">
      <div><div className="row-label">Traditional <b>shadow budget</b></div><Chain cls="chain--old" items={["Multiple spreadsheets", "Manual updates", "Fragmented records", "Limited visibility"]} /></div>
      <div><div className="row-label">FORGE <b>Financial Intelligence</b></div><Chain cls="chain--new" items={["Connected information", "Structured monitoring", "Reconciliation", "Forecasting", "Actionable visibility"]} /></div>
    </div>
  );
}
