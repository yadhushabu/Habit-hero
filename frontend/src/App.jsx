import { useEffect, useState } from "react";
import { checkInHabit, createHabit, deleteHabit, getHabits, downloadReport } from "./api/habits";
import HabitCard from "./components/HabitCard";
import HabitForm from "./components/HabitForm";
import GamificationSummary from "./components/GamificationSummary";
import "./App.css";

function App() {
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [gamificationKey, setGamificationKey] = useState(0); // forces GamificationSummary to refetch

  const loadHabits = async () => {
    try {
      const data = await getHabits();
      setHabits(data);
      setError(null);
    } catch (err) {
      setError("Could not reach the backend. Is the Django server running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHabits();
  }, []);

  const handleCreate = async (habitData) => {
    await createHabit(habitData);
    await loadHabits();
  };

  const handleCheckIn = async (habitId) => {
    await checkInHabit(habitId);
    await loadHabits();
    setGamificationKey((k) => k + 1); // refresh XP/badges after a check-in
  };

  const handleDelete = async (habitId) => {
    await deleteHabit(habitId);
    await loadHabits();
    setGamificationKey((k) => k + 1);
  };

  const handleDownloadReport = async () => {
    try {
      await downloadReport();
    } catch {
      setError("Could not download the report.");
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Habit Hero</h1>
        <p>Build better routines and stay consistent.</p>
      </header>

      <GamificationSummary key={gamificationKey} />

      <div className="toolbar">
        <button className="report-btn" onClick={handleDownloadReport}>
          Export PDF Report
        </button>
      </div>

      <HabitForm onCreate={handleCreate} />

      {error && <p className="error">{error}</p>}
      {loading && <p>Loading habits...</p>}

      <div className="habit-grid">
        {habits.map((habit) => (
          <HabitCard
            key={habit.id}
            habit={habit}
            onCheckIn={handleCheckIn}
            onDelete={handleDelete}
          />
        ))}
      </div>

      {!loading && habits.length === 0 && (
        <p className="empty-state">No habits yet — add your first one above.</p>
      )}
    </div>
  );
}

export default App;