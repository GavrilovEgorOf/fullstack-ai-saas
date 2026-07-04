let token = localStorage.getItem("token") || "";

async function api(path, opts = {}) {
  const headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
  if (token) headers.Authorization = "Bearer " + token;
  const r = await fetch(path, { ...opts, headers });
  return r.json();
}

document.getElementById("login")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const data = await api("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
  token = data.access_token;
  localStorage.setItem("token", token);
  document.getElementById("out").textContent = JSON.stringify(await api("/api/dashboard"), null, 2);
});

document.getElementById("ask")?.addEventListener("click", async () => {
  const question = document.getElementById("question").value;
  const data = await api("/api/ask", { method: "POST", body: JSON.stringify({ question }) });
  document.getElementById("out").textContent = JSON.stringify(data, null, 2);
});

if (token) {
  api("/api/dashboard").then((d) => {
    document.getElementById("out").textContent = JSON.stringify(d, null, 2);
  });
}
