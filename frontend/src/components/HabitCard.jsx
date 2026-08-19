function HabitCard({ habit, onCheckIn, onDelete }) {
  const today = new Date().toISOString().slice(0, 10);
  const checkedInToday = habit.checkins.some((c) => c.date === today);

  return (
    <div className="habit-card">
      <div className="habit-card-header">
        <h3>{habit.name}</h3>
        <span className="badge">{habit.category.replace("_", " ")}</span>
      </div>

      <div className="habit-stats">
        <div>
          <span className="stat-value">{habit.current_streak}</span>
          <span className="stat-label">current streak</span>
        </div>
        <div>
          <span className="stat-value">{habit.best_streak}</span>
          <span className="stat-label">best streak</span>
        </div>
        <div>
          <span className="stat-value">{habit.success_rate}%</span>
          <span className="stat-label">success rate</span>
        </div>
      </div>

      {habit.best_days.length > 0 && (
        <p className="best-days">Best days: {habit.best_days.join(", ")}</p>
      )}

      <div className="habit-actions">
        <button disabled={checkedInToday} onClick={() => onCheckIn(habit.id)}>
          {checkedInToday ? "Checked in today" : "Check in"}
        </button>
        <button className="danger" onClick={() => onDelete(habit.id)}>
          Delete
        </button>
      </div>
    </div>
  );
}

export default HabitCard;