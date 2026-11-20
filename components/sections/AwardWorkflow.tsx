const steps = [
  { t: "Award document", d: "An agreement or amendment is added to the workspace." },
  { t: "FORGE extraction", d: "Key terms are read into a draft record, each tied to its source page." },
  { t: "Validation", d: "An administrator reviews flagged and uncertain items and confirms." },
  { t: "Award record", d: "A structured record holds budget, dates, obligations and documents." },
  { t: "Monitoring & reminders", d: "Deadlines, balances and attention items are tracked from the record." },
];
export default function AwardWorkflow() {
  return (
    <div>
      <ol className="flow">{steps.map((s) => (<li key={s.t}><h3>{s.t}</h3><p>{s.d}</p></li>))}</ol>
      <p className="note note--blue" style={{ marginTop: 28 }}>Workflow design shown for illustration. Extraction and automation capabilities are in development, and a person validates every extracted value.</p>
    </div>
  );
}
