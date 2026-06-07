import { useState } from "react";
import Header from "./components/Header";
import UserTable from "./components/UserTable";
import SignalChart from "./components/SignalChart";
import AddUserModal from "./components/AddUserModal";
import Toast from "./components/Toast";
import { useUsers } from "./hooks/useUsers";
import "./App.css";

export default function App() {
  const { users, addUser, removeUser } = useUsers();
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleAddUser = (user) => {
    addUser(user);
    setShowModal(false);
    showToast(`${user.name} added to monitoring`);
  };

  const handleRemoveUser = (id, name) => {
    removeUser(id);
    showToast(`${name} removed`, "warning");
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
          <button className="btn-add" onClick={() => setShowModal(true)}>
            <span className="btn-icon">+</span>
            Add / Remove User
          </button>
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
