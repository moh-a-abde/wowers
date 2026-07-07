import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { fetchNational, fetchPlants, useAsync } from "../lib/data";
import type { PlantCollection } from "../lib/types";
import { BAND_COLOR, BAND_LABEL, TURBINE_LABEL } from "../lib/colors";
import { mwh, num, usd, years } from "../lib/format";
import KpiTile from "../components/KpiTile";
import MapView from "../components/MapView";
import { StateBar } from "../components/charts/Charts";

const TURBINES = ["Kaplan", "Francis", "Crossflow", "in_conduit_micro"];

export default function NationalMap() {
  const { data: national } = useAsync(fetchNational, []);
  const { data: plants } = useAsync(fetchPlants, []);

  const [state, setState] = useState("");
  const [turbines, setTurbines] = useState<string[]>([...TURBINES]);
  const [maxPayback, setMaxPayback] = useState(20);
  const [highOnly, setHighOnly] = useState(false);

  const filtered: PlantCollection | null = useMemo(() => {
    if (!plants) return null;
    const feats = plants.features.filter((f) => {
      const p = f.properties;
      if (state && p.state !== state) return false;
      if (p.turbine && !turbines.includes(p.turbine)) return false;
      if (highOnly && p.confidence !== "High") return false;
      if (p.payback == null) return false;
      return p.payback <= maxPayback;
    });
    return { type: "FeatureCollection", features: feats };
  }, [plants, state, turbines, maxPayback, highOnly]);

  const states = useMemo(
    () => (national ? national.by_state.map((s) => s.state).sort() : []),
    [national],
  );

  const toggleTurbine = (t: string) =>
    setTurbines((cur) => (cur.includes(t) ? cur.filter((x) => x !== t) : [...cur, t]));

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 22px", background: "#fff", borderBottom: "1px solid var(--border)" }}>
        <div>
          <div style={{ fontSize: 20, fontWeight: 800, color: "var(--navy)" }}>National Opportunity Map</div>
          <div className="muted" style={{ fontSize: 12 }}>Micro-hydro energy recovery across US wastewater plants</div>
        </div>
        {national && (
          <div className="kpi-row">
            <KpiTile value={num(national.plants_analyzed)} label="Plants Analyzed" />
            <KpiTile value={num(national.viable_projects)} label="Viable Projects" accent="var(--blue)" />
            <KpiTile value={usd(national.portfolio_npv_usd)} label="Portfolio NPV" accent="var(--green)" />
            <KpiTile value={years(national.median_payback)} label="Median Payback" />
          </div>
        )}
      </div>

      {/* body */}
      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        {/* filters */}
        <div style={{ width: 230, flexShrink: 0, background: "#fff", borderRight: "1px solid var(--border)", padding: 18, overflowY: "auto" }}>
          <h3 className="card-title">Filters</h3>

          <label className="muted" style={{ fontSize: 12, fontWeight: 600 }}>State</label>
          <select value={state} onChange={(e) => setState(e.target.value)} style={{ width: "100%", margin: "6px 0 10px" }}>
            <option value="">All States</option>
            {states.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          {state && (
            <Link to={`/state/${state}`} className="btn btn-blue" style={{ width: "100%", justifyContent: "center", marginBottom: 18 }}>
              View {state} Portfolio →
            </Link>
          )}

          <div className="muted" style={{ fontSize: 12, fontWeight: 600, marginBottom: 6 }}>Turbine Type</div>
          {TURBINES.map((t) => (
            <label key={t} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, padding: "3px 0" }}>
              <input type="checkbox" checked={turbines.includes(t)} onChange={() => toggleTurbine(t)} />
              {TURBINE_LABEL[t] ?? t}
            </label>
          ))}

          <div className="muted" style={{ fontSize: 12, fontWeight: 600, margin: "18px 0 6px" }}>
            Max Payback: {maxPayback} yr
          </div>
          <input type="range" min={1} max={20} value={maxPayback} onChange={(e) => setMaxPayback(+e.target.value)} style={{ width: "100%" }} />

          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, marginTop: 18 }}>
            <input type="checkbox" checked={highOnly} onChange={(e) => setHighOnly(e.target.checked)} />
            High confidence only
          </label>

          <div style={{ marginTop: 22, borderTop: "1px solid var(--border)", paddingTop: 14 }}>
            {(Object.keys(BAND_LABEL) as (keyof typeof BAND_LABEL)[]).map((b) => (
              <div key={b} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11, padding: "3px 0" }} className="muted">
                <span className="dot" style={{ background: BAND_COLOR[b] }} />
                {BAND_LABEL[b]}
              </div>
            ))}
          </div>
          {filtered && <div className="faint" style={{ fontSize: 11, marginTop: 14 }}>{num(filtered.features.length)} sites shown</div>}
        </div>

        {/* map */}
        <div style={{ flex: 1, minWidth: 0, position: "relative" }}>
          {filtered ? <MapView data={filtered} /> : <div className="loading">Loading map…</div>}
        </div>

        {/* top opportunities */}
        <div style={{ width: 300, flexShrink: 0, background: "#fff", borderLeft: "1px solid var(--border)", padding: 18, overflowY: "auto" }}>
          <h3 className="card-title">Top 5 Opportunities</h3>
          {national?.top_opportunities.map((o, i) => (
            <Link key={o.id} to={`/plant/${o.id}`} style={{ display: "block", color: "inherit" }}>
              <div style={{ display: "flex", gap: 10, padding: "10px 0", borderBottom: "1px solid #eef1f6" }}>
                <div style={{ width: 22, height: 22, borderRadius: 6, background: "var(--navy)", color: "#fff", fontSize: 12, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>{i + 1}</div>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: 13 }}>{o.name}</div>
                  <div className="muted" style={{ fontSize: 11 }}>{o.city}, {o.state}</div>
                  <div style={{ fontSize: 11, marginTop: 3 }}>
                    <span className="muted">Energy</span> {mwh(o.energy_mwh)} · <span className="muted">Payback</span> {years(o.payback)}
                  </div>
                </div>
              </div>
            </Link>
          ))}
          {national && (
            <>
              <h3 className="card-title" style={{ marginTop: 22 }}>Viable Sites by State</h3>
              <StateBar data={national.by_state.slice(0, 18)} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
