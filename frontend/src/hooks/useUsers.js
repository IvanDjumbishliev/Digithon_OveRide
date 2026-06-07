import { useState, useEffect } from "react";

const API = "http://localhost:5000/api/users";

export function useUsers() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch(API)
      .then((r) => r.json())
      .then(setUsers)
      .catch(() => setUsers([]));
  }, []);

  const addUser = async (user) => {
    const res = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: user.name, company: user.company, linkedin: user.linkedin }),
    });
    const saved = await res.json();
    setUsers((prev) => [saved, ...prev]);
  };

  const removeUser = async (id) => {
    await fetch(`${API}/${id}`, { method: "DELETE" });
    setUsers((prev) => prev.filter((u) => u.id !== id));
  };

  return { users, addUser, removeUser };
}
