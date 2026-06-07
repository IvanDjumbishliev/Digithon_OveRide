import "./Toast.css";

export default function Toast({ message, type }) {
  return (
    <div className={`toast toast-${type}`}>
      <span className="toast-icon">{type === "success" ? "✓" : "−"}</span>
      {message}
    </div>
  );
}
