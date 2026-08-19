const BASE_URL = "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
}

export function getHabits() {
  return request("/habits/");
}

export function createHabit(habit) {
  return request("/habits/", {
    method: "POST",
    body: JSON.stringify(habit),
  });
}

export function checkInHabit(habitId) {
  return request(`/habits/${habitId}/check_in/`, {
    method: "POST",
  });
}

export function deleteHabit(habitId) {
  return request(`/habits/${habitId}/`, { method: "DELETE" });
}

export function getGamificationSummary() {
  return request("/gamification/summary/");
}

export async function downloadReport() {
  const res = await fetch(`${BASE_URL}/habits/report/pdf/`);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "habit_progress_report.pdf";
  link.click();
  window.URL.revokeObjectURL(url);
}