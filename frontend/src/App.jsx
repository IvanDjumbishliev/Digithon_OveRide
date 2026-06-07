import { useState } from "react";
import Header from "./components/Header";
import UserTable from "./components/UserTable";
import SignalChart from "./components/SignalChart";
import AddUserModal from "./components/AddUserModal";
import Toast from "./components/Toast";
import ResultPage from "./components/ResultPage";
import { useUsers } from "./hooks/useUsers";
import "./App.css";

export default function App() {
  if (new URLSearchParams(window.location.search).get("status")) {
    return <ResultPage />;
  }
  const { users, addUser, removeUser } = useUsers();
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [toast, setToast] = useState(null);
  const [syncing, setSyncing] = useState(false);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleAddUser = async (user) => {
    await addUser(user);
    setShowModal(false);
    showToast(`${user.name} added to monitoring`);
  };

  const handleRemoveUser = (id, name) => {
    removeUser(id);
    showToast(`${name} removed`, "warning");
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      const resp = await fetch("http://localhost:5000/api/run-pipeline", { method: "POST" });
      const data = await resp.json();
      if (data.ok) {
        showToast(`Sync complete — ${data.alerts} alert(s) sent to Discord`);
      } else {
        showToast(data.error || "Sync failed", "warning");
      }
    } catch {
      showToast("Cannot reach server on :5000", "warning");
    } finally {
      setSyncing(false);
    }
  };

  const filtered = users.filter(
    (u) =>
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.company.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="app">
      <Header search={search} onSearch={setSearch} users={users} />

      <main className="main">
        <div className="section-header">
          <div className="section-meta">
            <span className="section-label">Monitored Accounts</span>
            <span className="count-badge">{users.length}</span>
          </div>
          <div className="section-actions">
            <button className="btn-sync" onClick={handleSync} disabled={syncing}>
              {syncing ? <><span className="spin">⟳</span> Syncing…</> : "⟳ Sync"}
            </button>
            <button className="btn-add" onClick={() => setShowModal(true)}>
              <span className="btn-icon">+</span>
              Add / Remove User
            </button>
          </div>
        </div>

        <UserTable users={filtered} onRemove={handleRemoveUser} />
        <SignalChart users={users} />
      </main>

      {showModal && (
        <AddUserModal
          onAdd={handleAddUser}
          onClose={() => setShowModal(false)}
          onRemove={handleRemoveUser}
          users={users}
        />
      )}

      {toast && <Toast message={toast.message} type={toast.type} />}
    </div>
  );
}
