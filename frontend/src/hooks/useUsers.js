import { useState } from "react";

const SEED_USERS = [
  {
    id: 1,
    name: "Maria Ivanova",
    company: "TechFlow BG",
    linkedin: "linkedin.com/in/mariaivanova",
    signal: "upsell",
    lastScan: "2 min ago",
  },
  {
    id: 2,
    name: "Georgi Petrov",
    company: "SoftServe Ltd",
    linkedin: "linkedin.com/in/gpetrov",
    signal: "churn",
    lastScan: "14 min ago",
  },
  {
    id: 3,
    name: "Elena Todorova",
    company: "Bright Systems",
    linkedin: "linkedin.com/in/elenatodorova",
    signal: "neutral",
    lastScan: "1 hr ago",
  },
  {
    id: 4,
    name: "Dimitar Kolev",
    company: "DataWave EOOD",
    linkedin: "linkedin.com/in/dkolev",
    signal: "upsell",
    lastScan: "3 hr ago",
  },
];

export function useUsers() {
  const [users, setUsers] = useState(SEED_USERS);

  const addUser = (user) => {
    setUsers((prev) => [user, ...prev]);
  };

  const removeUser = (id) => {
    setUsers((prev) => prev.filter((u) => u.id !== id));
  };

  return { users, addUser, removeUser };
}
