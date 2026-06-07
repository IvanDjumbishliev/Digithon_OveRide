import { useMemo } from "react";
import "./SignalChart.css";

const WEEKS = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"];

function generateTrend(seed, length) {
  let v = (seed % 5) + 3;
  return Array.from({ length }, () => {
    v = Math.max(1, Math.min(10, v + (Math.random() - 0.5) * 3));
    return Math.round(v);
  });
}

export default function SignalChart({ users }) {
  const chartData = useMemo(() => {
    const upsellData = WEEKS.map((_, i) =>
      users.filter((u) => u.signal === "upsell").length + Math.round(Math.sin(i * 0.8) * 1.5)
    );
    const churnData = WEEKS.map((_, i) =>
      users.filter((u) => u.signal === "churn").length + Math.round(Math.cos(i * 0.6) * 1)
    );
    return { upsellData, churnData };
  }, [users]);

  const maxVal = Math.max(...chartData.upsellData, ...chartData.churnData, 1);

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div>
          <h3 className="chart-title">Signal Trends</h3>
          <p className="chart-subtitle">8-week rolling window · LinkedIn activity analysis</p>
        </div>
        <div className="chart-legend">
          <span className="legend-item green">
            <span className="legend-dot"></span> Upsell opportunities
          </span>
          <span className="legend-item red">
            <span className="legend-dot"></span> Churn risk signals
          </span>
        </div>
      </div>

      <div className="chart-body">
        <div className="bar-chart">
          {WEEKS.map((week, i) => (
            <div key={week} className="bar-group">
              <div className="bars">
                <div
                  className="bar bar-green"
                  style={{ height: `${(chartData.upsellData[i] / maxVal) * 100}%` }}
                  title={`Upsell: ${chartData.upsellData[i]}`}
                />
                <div
                  className="bar bar-red"
                  style={{ height: `${(chartData.churnData[i] / maxVal) * 100}%` }}
                  title={`Churn: ${chartData.churnData[i]}`}
                />
              </div>
              <span className="bar-label">{week}</span>
            </div>
          ))}
        </div>
        <div className="chart-y-axis">
          {[maxVal, Math.round(maxVal / 2), 0].map((v) => (
            <span key={v} className="y-label">{v}</span>
          ))}
        </div>
      </div>

      <div className="chart-footer">
        <div className="insight-card insight-green">
          <span className="insight-icon">↑</span>
          <div>
            <div className="insight-title">Trending Up</div>
            <div className="insight-desc">Upsell signals +23% this week</div>
          </div>
        </div>
        <div className="insight-card insight-red">
          <span className="insight-icon">⚠</span>
          <div>
            <div className="insight-title">Watch List</div>
            <div className="insight-desc">2 accounts showing exit signals</div>
          </div>
        </div>
        <div className="insight-card insight-purple">
          <span className="insight-icon">✉</span>
          <div>
            <div className="insight-title">Drafts Ready</div>
            <div className="insight-desc">5 emails awaiting Discord approval</div>
          </div>
        </div>
      </div>
    </div>
  );
}
