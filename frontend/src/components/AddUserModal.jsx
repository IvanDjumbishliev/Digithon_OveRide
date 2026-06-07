import { useState } from "react";
import "./AddUserModal.css";

export default function AddUserModal({ onAdd, onClose, onRemove, users }) {
  const [tab, setTab] = useState("add");
  const [form, setForm] = useState({ name: "", company: "", linkedin: "" });
  const [errors, setErrors] = useState({});

  const validate = () => {
    const e = {};
    if (!form.name.trim()) e.name = "Name is required";
    if (!form.company.trim()) e.company = "Company is required";
    if (!form.linkedin.trim()) e.linkedin = "LinkedIn URL is required";
    else if (!form.linkedin.includes("linkedin")) e.linkedin = "Must be a LinkedIn URL";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) return;
    onAdd({
      id: Date.now(),
      name: form.name.trim(),
      company: form.company.trim(),
      linkedin: form.linkedin.trim(),
      signal: "neutral",
      lastScan: "Just added",
    });
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h2 className="modal-title">Manage Users</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-tabs">
          <button
            className={`modal-tab ${tab === "add" ? "active" : ""}`}
            onClick={() => setTab("add")}
          >
            Add User
          </button>
          <button
            className={`modal-tab ${tab === "remove" ? "active" : ""}`}
            onClick={() => setTab("remove")}
          >
            Remove User
            {users.length > 0 && <span className="tab-count">{users.length}</span>}
          </button>
        </div>

        {tab === "add" && (
          <div className="modal-body">
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                placeholder="e.g. John Smith"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className={errors.name ? "error" : ""}
              />
              {errors.name && <span className="error-msg">{errors.name}</span>}
            </div>

            <div className="form-group">
              <label>Company</label>
              <input
                type="text"
                placeholder="e.g. Acme Corp"
                value={form.company}
                onChange={(e) => setForm({ ...form, company: e.target.value })}
                className={errors.company ? "error" : ""}
              />
              {errors.company && <span className="error-msg">{errors.company}</span>}
            </div>

            <div className="form-group">
              <label>LinkedIn URL</label>
              <input
                type="url"
                placeholder="linkedin.com/in/johnsmith"
                value={form.linkedin}
                onChange={(e) => setForm({ ...form, linkedin: e.target.value })}
                className={errors.linkedin ? "error" : ""}
              />
              {errors.linkedin && <span className="error-msg">{errors.linkedin}</span>}
            </div>

            <div className="modal-actions">
              <button className="btn-cancel" onClick={onClose}>Cancel</button>
              <button className="btn-confirm" onClick={handleSubmit}>
                Start Monitoring
              </button>
            </div>
          </div>
        )}

        {tab === "remove" && (
          <div className="modal-body">
            {users.length === 0 ? (
              <div className="remove-empty">No users to remove</div>
            ) : (
              <div className="remove-list">
                {users.map((u) => (
                  <div key={u.id} className="remove-row">
                    <div className="remove-info">
                      <span className="remove-name">{u.name}</span>
                      <span className="remove-company">{u.company}</span>
                    </div>
                    <button
                      className="btn-remove-confirm"
                      onClick={() => { onRemove(u.id, u.name); }}
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
