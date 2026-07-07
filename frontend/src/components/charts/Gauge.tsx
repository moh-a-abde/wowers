/* Semicircular gauge for P10 / P50 / P90 energy recovery.
   Scale spans exactly P10 (left end) to P90 (right end) so the axis
   labels match the arc endpoints. */
export default function Gauge({
  p10,
  p50,
  p90,
  unit = "MWh/yr",
}: {
  p10: number;
  p50: number;
  p90: number;
  unit?: string;
}) {
  const W = 320;
  const H = 180;
  const cx = W / 2;
  const cy = 160;
  const r = 130;
  const lo = p10;
  const hi = p90;
  const frac = hi > lo ? Math.min(1, Math.max(0, (p50 - lo) / (hi - lo))) : 0.5;
  const angle = Math.PI * (1 - frac); // pi (left) -> 0 (right)
  const nx = cx + r * Math.cos(angle);
  const ny = cy - r * Math.sin(angle);

  const arc = (startFrac: number, endFrac: number, color: string) => {
    const a0 = Math.PI * (1 - startFrac);
    const a1 = Math.PI * (1 - endFrac);
    const x0 = cx + r * Math.cos(a0), y0 = cy - r * Math.sin(a0);
    const x1 = cx + r * Math.cos(a1), y1 = cy - r * Math.sin(a1);
    const large = endFrac - startFrac > 0.5 ? 1 : 0;
    return <path d={`M ${x0} ${y0} A ${r} ${r} 0 ${large} 1 ${x1} ${y1}`} stroke={color} strokeWidth={16} fill="none" strokeLinecap="round" />;
  };

  return (
    <div style={{ textAlign: "center" }}>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ maxWidth: 340 }}>
        {arc(0, 0.5, "#7aa7f0")}
        {arc(0.5, 1, "#2bb673")}
        <line x1={cx} y1={cy} x2={nx} y2={ny} stroke="#0f1b2d" strokeWidth={4} strokeLinecap="round" />
        <circle cx={cx} cy={cy} r={7} fill="#0f1b2d" />
        <text x={cx - r} y={cy + 18} fontSize={11} fill="#5b6b80" textAnchor="middle">P10</text>
        <text x={cx + r} y={cy + 18} fontSize={11} fill="#5b6b80" textAnchor="middle">P90</text>
      </svg>
      <div style={{ marginTop: -8 }}>
        <div style={{ fontSize: 30, fontWeight: 800, color: "#0f1b2d", lineHeight: 1 }}>
          {Math.round(p50).toLocaleString()}
        </div>
        <div className="muted" style={{ fontSize: 12 }}>P50 · {unit}</div>
      </div>
    </div>
  );
}
