import { useEffect, useState } from "react";
import { getGamificationSummary } from "../api/habits";

function GamificationSummary() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    getGamificationSummary().then(setSummary).catch(() => setSummary(null));
  }, []);

  if (!summary) return null;

  const progressPercent = (summary.xp_into_level / summary.xp_for_next_level) * 100;

  return (
    <div className="gamification-panel">
      <div className="level-row">
        <span className="level-label">Level {summary.level}</span>
        <span className="xp-label">{summary.total_xp} XP total</span>
      </div>

      <div className="xp-bar">
        <div className="xp-bar-fill" style={{ width: `${progressPercent}%` }} />
      </div>
      <p className="xp-caption">
        {summary.xp_into_level} / {summary.xp_for_next_level} XP to next level
      </p>

      {summary.badges.length > 0 && (
        <div className="badge-shelf">
          {summary.badges.map((b) => (
            <div key={b.code} className="badge-item" title={b.description}>
              <span className="badge-icon">{b.icon}</span>
              <span className="badge-name">{b.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default GamificationSummary;