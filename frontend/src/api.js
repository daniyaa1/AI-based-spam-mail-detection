const isLocalDev =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost";

const BASE = import.meta.env.VITE_API_BASE_URL || (
  isLocalDev ? "http://127.0.0.1:8000" : "/api"
);

export async function analyzeText(subject, body) {
  const res = await fetch(`${BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subject, body }),
  });

  if (!res.ok) {
    throw new Error("Analysis failed");
  }

  return res.json();
}

export async function getModelInfo() {
  const res = await fetch(`${BASE}/model-info`);

  if (!res.ok) {
    throw new Error("Failed to load model info");
  }

  return res.json();
}
