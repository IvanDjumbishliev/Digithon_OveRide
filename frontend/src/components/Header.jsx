import "./Header.css";

export default function Header({ search, onSearch }) {
  return (
    <header className="header">
      <div className="header-top">
        <div className="logo-area">
          <div className="logo-mark">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
              <circle cx="11" cy="11" r="10" stroke="#6c63ff" strokeWidth="1.5" />
              <path d="M7 11 L11 7 L15 11 L11 15 Z" fill="#6c63ff" />
            </svg>
          </div>
          <div>
            <span className="logo-text">SIGNAL</span>
            <span className="logo-sub">LinkedIn Intelligence Agent</span>
          </div>
        </div>

        <div className="stat-pills">
          <div className="stat-pill churn">
            <span className="pill-label">CHURN RISK</span>
            <span className="pill-value">3</span>
            <span className="pill-pct">12%</span>
          </div>
          <div className="stat-pill upsell">
            <span className="pill-label">UPSELL OPP</span>
            <span className="pill-value">7</span>
            <span className="pill-pct">28%</span>
          </div>
          <div className="status-dot">
            <span className="dot pulse"></span>
            <span className="dot-label">Agent Active</span>
          </div>
        </div>
      </div>

      <div className="search-wrap">
        <div className="search-bar">
          <svg className="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="7" cy="7" r="5" stroke="#6b6b88" strokeWidth="1.5" />
            <path d="M11 11 L14 14" stroke="#6b6b88" strokeWidth="1.5" strokeLinecap="round" />
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
    </header>
  );
}
