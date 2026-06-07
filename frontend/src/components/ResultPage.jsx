import "./ResultPage.css";

export default function ResultPage() {
  const params = new URLSearchParams(window.location.search);
  const status = params.get("status");
  const company = params.get("company") || "";
  const contact = params.get("contact") || "";
  const subject = params.get("subject") || "";
  const score = params.get("score") || "";
  const sentTo = params.get("sentTo") || "";

  const isApproved = status === "approved";

  return (
    <div className="result-page">
      <div className="result-card">
        <div className={`result-icon-wrap ${isApproved ? "approved" : "declined"}`}>
          {isApproved ? (
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          ) : (
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          )}
        </div>

        <h1 className="result-heading">
          {isApproved ? "Email Approved & Sent" : "Email Declined"}
        </h1>
        <p className="result-sub">
          {isApproved
            ? `The outreach email was sent successfully to ${sentTo}`
            : "The email was not sent. The alert has been marked as declined."}
        </p>

        <div className="result-divider" />

        <div className="result-details">
          <div className="result-row">
            <span className="result-label">Company</span>
            <span className="result-value">{company}</span>
          </div>
          {contact && (
            <div className="result-row">
              <span className="result-label">Contact</span>
              <span className="result-value">{contact}</span>
            </div>
          )}
          {subject && (
            <div className="result-row">
              <span className="result-label">Subject</span>
              <span className="result-value">{subject}</span>
            </div>
          )}
          {score && (
            <div className="result-row">
              <span className="result-label">Risk Score</span>
              <span className={`result-score ${isApproved ? "green" : "red"}`}>{score}/100</span>
            </div>
          )}
        </div>

        <a href="/" className="result-back">
          ← Back to Dashboard
        </a>
      </div>
    </div>
  );
}
