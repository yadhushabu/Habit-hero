import { useState } from "react";

const FREQUENCIES = ["daily", "weekly"];
const CATEGORIES = ["health", "work", "learning", "fitness", "mental_health", "productivity"];

function HabitForm({ onCreate }) {
  const [name, setName] = useState("");
  const [frequency, setFrequency] = useState("daily");
  const [category, setCategory] = useState("health");
  const [startDate, setStartDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSubmitting(true);
    try {
      await onCreate({ name, frequency, category, start_date: startDate });
      setName("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="New habit name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <select value={frequency} onChange={(e) => setFrequency(e.target.value)}>
        {FREQUENCIES.map((f) => (
          <option key={f} value={f}>{f}</option>
        ))}
      </select>
      <select value={category} onChange={(e) => setCategory(e.target.value)}>
        {CATEGORIES.map((c) => (
          <option key={c} value={c}>{c.replace("_", " ")}</option>
        ))}
      </select>
      <input
        type="date"
        value={startDate}
        onChange={(e) => setStartDate(e.target.value)}
      />
      <button type="submit" disabled={submitting}>
        {submitting ? "Adding..." : "Add habit"}
      </button>
    </form>
  );
}

export default HabitForm;