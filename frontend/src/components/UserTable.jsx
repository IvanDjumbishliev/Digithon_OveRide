import "./UserTable.css";

const SIGNAL_CONFIG = {
  upsell: { label: "Upsell", color: "green", icon: "↑" },
  churn: { label: "Churn Risk", color: "red", icon: "⚠" },
  neutral: { label: "Neutral", color: "yellow", icon: "–" },
};

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
  const colors = ["#6c63ff", "#00d68f", "#ff4d6d", "#ffd166", "#00b4d8"];
  const color = colors[name.charCodeAt(0) % colors.length];
  return (
    <div className="avatar" style={{ "--av-color": color }}>
      {initials}
    </div>
  );
}

export default function UserTable({ users, onRemove }) {
  if (users.length === 0) {
    return (
      <div className="table-empty">
        <span>No accounts monitored yet — add your first user</span>
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table className="user-table">
        <thead>
          <tr>
            <th>USER</th>
            <th>COMPANY</th>
            <th>LINKEDIN</th>
            <th>SIGNAL</th>
            <th>LAST SCAN</th>
            <th>DRAFT EMAIL</th>
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
              <td>
                <span className="company-name">{u.company}</span>
              </td>
              <td>
                <a
                  href={u.linkedin.startsWith("http") ? u.linkedin : `https://${u.linkedin}`}
                  target="_blank"
                  rel="noreferrer"
                  className="li-link"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z M4 6a2 2 0 1 1 0-4 2 2 0 0 1 0 4z" />
                  </svg>
                  Profile
                </a>
              </td>
              <td><SignalBadge signal={u.signal} /></td>
              <td><span className="scan-time">{u.lastScan}</span></td>
              <td>
                <button className="btn-draft" title="View AI draft email">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                  View Draft
                </button>
              </td>
              <td>
                <button
                  className="btn-remove"
                  onClick={() => onRemove(u.id, u.name)}
                  title="Remove user"
                >
                  ✕
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
