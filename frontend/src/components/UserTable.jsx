import "./UserTable.css";

const SIGNAL_CONFIG = {
  upsell: { label: "Upsell ready", color: "green", icon: "↑" },
  churn: { label: "Churn risk", color: "red", icon: "⚠" },
  neutral: { label: "Watching", color: "yellow", icon: "·" },
};

const AVATAR_PALETTES = [
  { bg: "#e8f0fe", border: "#c5d8fd", text: "#2d5be3" },
  { bg: "#edf7f2", border: "#b6e3cc", text: "#1a7a4a" },
  { bg: "#fdf2f1", border: "#f0c4be", text: "#c0392b" },
  { bg: "#fef8ee", border: "#f0dca0", text: "#92600a" },
  { bg: "#f5f0fe", border: "#d8c8fb", text: "#6b3fd4" },
];

function SignalBadge({ signal }) {
  const cfg = SIGNAL_CONFIG[signal] || SIGNAL_CONFIG.neutral;
  return (
    <span className={`signal-badge signal-${cfg.color}`}>
      <span>{cfg.icon}</span> {cfg.label}
    </span>
  );
}

function Avatar({ name }) {
  const initials = name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  const p = AVATAR_PALETTES[name.charCodeAt(0) % AVATAR_PALETTES.length];
  return (
    <div className="avatar" style={{ "--av-bg": p.bg, "--av-border": p.border, "--av-text": p.text }}>
      {initials}
    </div>
  );
}

export default function UserTable({ users, onRemove }) {
  if (users.length === 0) {
    return <div className="table-empty">No accounts monitored yet — add your first user above</div>;
  }

  return (
    <div className="table-wrap">
      <table className="user-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Company</th>
            <th>LinkedIn</th>
            <th>Signal</th>
            <th>Last Scan</th>
            <th>Draft Email</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} className="user-row">
              <td>
                <div className="user-cell">
                  <Avatar name={u.name} />
                  <span className="user-name">{u.name}</span>
                </div>
              </td>
              <td><span className="company-name">{u.company}</span></td>
              <td>
                <a
                  href={u.linkedin.startsWith("http") ? u.linkedin : `https://${u.linkedin}`}
                  target="_blank"
                  rel="noreferrer"
                  className="li-link"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z M4 6a2 2 0 1 1 0-4 2 2 0 0 1 0 4z" />
                  </svg>
                  View
                </a>
              </td>
              <td><SignalBadge signal={u.signal} /></td>
              <td><span className="scan-time">{u.lastScan}</span></td>
              <td>
                <button className="btn-draft">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                  View Draft
                </button>
              </td>
              <td>
                <button className="btn-remove" onClick={() => onRemove(u.id, u.name)}>✕</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
