const BASE = "/api";

function sessionParam() {
  const s = localStorage.getItem("session");
  return s ? `?session=${s}` : "";
}

export async function getLoginUrl() {
  const res = await fetch(`${BASE}/auth/login`);
  const data = await res.json();
  return data.url;
}

export async function getMe() {
  const res = await fetch(`${BASE}/auth/me${sessionParam()}`);
  if (!res.ok) throw new Error("Not authenticated");
  return res.json();
}

export async function logout() {
  await fetch(`${BASE}/auth/logout${sessionParam()}`, { method: "POST" });
  localStorage.removeItem("session");
}

export async function fetchEmails(maxResults = 30) {
  const session = localStorage.getItem("session");
  const res = await fetch(
    `${BASE}/emails?session=${session}&max_results=${maxResults}`
  );
  if (!res.ok) throw new Error("Failed to fetch emails");
  return res.json();
}

export async function analyzeText(subject, body) {
  const res = await fetch(`${BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subject, body }),
  });
  if (!res.ok) throw new Error("Analysis failed");
  return res.json();
}
