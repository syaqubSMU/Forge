import { systemsLeft, workspaceItems, usersRight } from "@/lib/content";

/** Operating model: university systems → connection layer → FORGE workspace → users. Architecture intent only. */
export default function IntegrationDiagram({ tone = "light" }: { tone?: "light" }) {
  void tone;
  return (
    <div>
      <div className="intg" role="group" aria-label="FORGE operating model">
        <div className="col"><h3>University systems</h3><ul>{systemsLeft.map((s) => <li key={s}>{s}</li>)}</ul></div>
        <div className="conn" aria-hidden="true"><span>Approved imports, exports &amp; APIs</span></div>
        <div className="col col--core"><h3>FORGE workspace</h3><ul>{workspaceItems.map((s) => <li key={s}>{s}</li>)}</ul></div>
        <div className="conn" aria-hidden="true"><span>Role-based views</span></div>
        <div className="col"><h3>Users</h3><ul>{usersRight.map((s) => <li key={s}>{s}</li>)}</ul></div>
      </div>
      <p className="note" style={{ marginTop: 24 }}>
        FORGE is designed to work alongside existing institutional systems through approved integrations, data imports, exports and APIs. Specific integrations are not claimed as operational until they are built and verified. Named systems are trademarks of their respective owners; FORGE is not affiliated with or endorsed by them.
      </p>
    </div>
  );
}
