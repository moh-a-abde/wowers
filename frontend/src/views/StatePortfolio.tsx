import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchPortfolio, useAsync } from "../lib/data";
import type { TableRow } from "../lib/types";
import { BAND_COLOR, CONF_PILL } from "../lib/colors";
import { num, usd, years } from "../lib/format";
import { EnergyBar, RiskReturn } from "../components/charts/Charts";

type Key = keyof TableRow;
const COLS: { key: Key; label: string; n?: boolean }[] = [
  { key: "rank", label: "Rank" },
  { key: "name", label: "Plant Name" },
  { key: "city", label: "City" },
  { key: "flow_mgd", label: "Flow (MGD)", n: true },
  { key: "turbine", label: "Turbine" },
  { key: "capex_usd", label: "CapEx", n: true },
  { key: "annual_savings_usd", label: "Annual Savings", n: true },
  { key: "payback", label: "Payback", n: true },
  { key: "npv_usd", label: "NPV", n: true },
  { key: "confidence", label: "Confidence" },
];

export default function StatePortfolio() {
  const { code = "" } = useParams();
  const { data, error } = useAsync(() => fetchPortfolio(code), [code]);
  const [sort, setSort] = useState<{ key: Key; dir: 1 | -1 }>({ key: "npv_usd", dir: -1 });
  const [q, setQ] = useState("");

  const rows = useMemo(() => {
    if (!data) return [];
    let r = data.rows;
    if (q) r = r.filter((x) => (x.name ?? "").toLowerCase().includes(q.toLowerCase()) || (x.city ?? "").toLowerCase().includes(q.toLowerCase()));
    return [...r].sort((a, b) => {
      const av = a[sort.key], bv = b[sort.key];
      if (av == null) return 1;
      if (bv == null) return -1;
      return av > bv ? sort.dir : av < bv ? -sort.dir : 0;
    });
  }, [data, sort, q]);

  const energyData = useMemo(
    () => rows.slice(0, 10).map((r) => ({ name: r.name ?? r.id, mwh: r.energy_mwh ?? 0 })),
    [rows],
  );
  const scatterData = useMemo(
    () => rows.filter((r) => r.payback != null && r.npv_usd != null)
      .map((r) => ({ payback: r.payback!, npv: r.npv_usd!, band: r.band, name: r.name ?? r.id })),
    [rows],
  );

  if (error) return <div className="loading">No portfolio data for “{code}”. <Link to="/">← Back to map</Link></div>;
  if (!data) return <div className="loading">Loading {code} portfolio…</div>;

  const setKey = (key: Key) =>
    setSort((s) => (s.key === key ? { key, dir: (-s.dir) as 1 | -1 } : { key, dir: -1 }));

  return (
    <div style={{ padding: 22 }}>
      <Link to="/" className="muted" style={{ fontSize: 12 }}>← National map</Link>
      <h1 style={{ fontSize: 26, fontWeight: 800, color: "var(--navy)", margin: "8px 0 2px" }}>
        Portfolio Analysis — {data.state}
      </h1>
      <div className="muted" style={{ fontSize: 14, marginBottom: 18 }}>
        {num(data.n_viable)} viable sites &nbsp;|&nbsp; {usd(data.combined_npv_usd)} combined NPV &nbsp;|&nbsp; {usd(data.annual_savings_usd)}/yr savings
      </div>

      <div style={{ display: "flex", gap: 18, alignItems: "flex-start" }}>
        <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: 18 }}>
          {/* table */}
          <div className="card card-pad">
            <input type="text" placeholder="Search plants…" value={q} onChange={(e) => setQ(e.target.value)} style={{ width: 240, marginBottom: 12 }} />
            <div style={{ overflowX: "auto" }}>
              <table className="tbl">
                <thead>
                  <tr>
                    {COLS.map((c) => (
                      <th key={c.key} className={c.n ? "num" : ""} onClick={() => setKey(c.key)}>
                        {c.label}{sort.key === c.key ? (sort.dir === -1 ? " ▾" : " ▴") : ""}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.slice(0, 100).map((r) => (
                    <tr key={r.id}>
                      <td>{r.rank}</td>
                      <td><Link to={`/plant/${r.id}`}>{r.name}</Link></td>
                      <td>{r.city}</td>
                      <td className="num">{num(r.flow_mgd)}</td>
                      <td>{r.turbine}</td>
                      <td className="num">{usd(r.capex_usd)}</td>
                      <td className="num">{usd(r.annual_savings_usd)}</td>
                      <td className="num">{years(r.payback)}</td>
                      <td className="num">{usd(r.npv_usd)}</td>
                      <td><span className={`pill ${CONF_PILL[r.confidence]}`}><span className="dot" style={{ background: BAND_COLOR[r.band] }} />{r.confidence}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {rows.length > 100 && <div className="faint" style={{ fontSize: 11, marginTop: 8 }}>Showing top 100 of {num(rows.length)}.</div>}
          </div>

          {/* charts */}
          <div style={{ display: "flex", gap: 18 }}>
            <div className="card card-pad" style={{ flex: 1, minWidth: 0 }}>
              <h3 className="card-title">Annual Energy by Site (Top 10)</h3>
              <EnergyBar data={energyData} />
            </div>
            <div className="card card-pad" style={{ flex: 1, minWidth: 0 }}>
              <h3 className="card-title">Risk vs Return — {data.state}</h3>
              <RiskReturn data={scatterData} />
            </div>
          </div>
        </div>

        {/* summary sidebar */}
        <div className="card card-pad" style={{ width: 250, flexShrink: 0 }}>
          <h3 className="card-title">Portfolio Summary</h3>
          {[
            ["Viable sites", num(data.n_viable)],
            ["Total CapEx", usd(data.total_capex_usd)],
            ["Combined NPV", usd(data.combined_npv_usd)],
            ["Annual savings", `${usd(data.annual_savings_usd)}/yr`],
            ["Avg payback", years(data.avg_payback)],
            ["High-confidence", `${num(data.high_confidence_sites)} (${data.n_viable ? Math.round((data.high_confidence_sites / data.n_viable) * 100) : 0}%)`],
          ].map(([l, v]) => (
            <div key={l} style={{ padding: "11px 0", borderBottom: "1px solid #eef1f6" }}>
              <div className="muted" style={{ fontSize: 12 }}>{l}</div>
              <div style={{ fontSize: 19, fontWeight: 700, color: "var(--navy)" }}>{v}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
