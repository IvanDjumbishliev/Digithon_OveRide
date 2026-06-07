import "./Header.css";

const CHIPS = [
  { label: "Churn signals", icon: "⚠" },
  { label: "Upsell ready", icon: "↑" },
  { label: "Job change", icon: "👤" },
  { label: "New funding", icon: "💰" },
  { label: "Competitor switch", icon: "⚡" },
];

export default function Header({ search, onSearch, users }) {
  const churnCount = users.filter(u => u.signal === "churn").length;
  const upsellCount = users.filter(u => u.signal === "upsell").length;

  return (
    <header className="header">
      <div className="topnav">
        <div className="logo-area">
          <div className="logo-mark">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M9 2L15 6V12L9 16L3 12V6L9 2Z" fill="white" />
            </svg>
          </div>
          <div>
            <span className="logo-text">OveRide Signal</span>
          </div>
        </div>
        <div className="nav-status">
          <span className="dot pulse"></span>
          Agent scanning LinkedIn
        </div>
      </div>

      <div className="hero">
        <div className="hero-badge">
          <span className="badge-dot">AI</span>
          Monitors LinkedIn · Detects intent · Drafts outreach
        </div>

        <h1 className="hero-title">
          Know when to reach out,<br /><em>before it's too late</em>
        </h1>
        <p className="hero-sub">
          Your agent scans key accounts for buying signals and churn risk — then writes the perfect email.
        </p>

        <div className="search-wrap">
          <div className="search-bar">
            <svg className="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5" />
              <path d="M11 11 L14 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
            <input
              type="text"
              placeholder="Search by name or company..."
              value={search}
              onChange={(e) => onSearch(e.target.value)}
            />
            {search && (
              <button className="search-clear" onClick={() => onSearch("")}>✕</button>
            )}
          </div>
        </div>

        <div className="filter-chips">
          {CHIPS.map(c => (
            <button key={c.label} className="chip">
              <span className="chip-icon">{c.icon}</span>
              {c.label}
            </button>
          ))}
        </div>

        <div className="stat-bar">
          <div className="stat-item">
            <span className="stat-num">{users.length}</span>
            <span className="stat-lbl">Monitored</span>
          </div>
          <div className="stat-item churn">
            <span className="stat-num">{churnCount}</span>
            <span className="stat-lbl">Churn Risk</span>
          </div>
          <div className="stat-item upsell">
            <span className="stat-num">{upsellCount}</span>
            <span className="stat-lbl">Upsell Ready</span>
          </div>
          <div className="stat-item">
            <span className="stat-num">4</span>
            <span className="stat-lbl">Drafts Pending</span>
          </div>
        </div>
      </div>
    </header>
  );
}
