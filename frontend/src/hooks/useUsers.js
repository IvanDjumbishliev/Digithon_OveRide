import { useState, useEffect } from "react";

const API_URL = "http://localhost:5000/api/users";

export function useUsers() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch(API_URL)
      .then((r) => r.json())
      .then((data) => setUsers(data))
      .catch(() => setUsers([]));
  }, []);

  const addUser = (user) => {
    setUsers((prev) => [user, ...prev]);
  };

  const removeUser = (id) => {
    setUsers((prev) => prev.filter((u) => u.id !== id));
  };

  return { users, addUser, removeUser };
}
