/** Dashboard-style placeholder illustration (not a real screenshot). */
export default function ProductMock({ label }: { label: string }) {
  return (
    <div className="pmock" role="img" aria-label={`Illustrative preview of ${label}`}>
      <div className="hd" /><div className="ln" /><div className="ln t" /><div className="ln" /><div className="ln c" />
      <div className="tag">Illustrative preview</div>
    </div>
  );
}
