"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { api, clearToken, getToken } from "@/lib/api";

type Dashboard = {
  email: string;
  workspace: string;
  plan: string;
  queries_used: number;
  queries_limit: number;
  knowledge_entries: number;
};

type Doc = { id: string; title: string; content: string; status: string; created_at: string };
type History = { id: number; question: string; answer: string; created_at: string };

export default function DashboardPage() {
  const router = useRouter();
  const token = getToken();
  const [dash, setDash] = useState<Dashboard | null>(null);
  const [docs, setDocs] = useState<Doc[]>([]);
  const [history, setHistory] = useState<History[]>([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (!token) {
      router.replace("/login");
      return;
    }
    void load();
  }, [token, router]);

  async function load() {
    if (!token) return;
    const [d, k, h] = await Promise.all([
      api<Dashboard>("/api/dashboard", { token }),
      api<Doc[]>("/api/knowledge", { token }),
      api<History[]>("/api/history", { token }),
    ]);
    setDash(d);
    setDocs(k);
    setHistory(h);
  }

  async function ask(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setMsg("");
    try {
      const res = await api<{ answer: string }>("/api/ask", {
        method: "POST",
        token,
        body: JSON.stringify({ question }),
      });
      setAnswer(res.answer);
      await load();
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Ask failed");
    }
  }

  async function addDoc(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    await api("/api/knowledge", {
      method: "POST",
      token,
      body: JSON.stringify({ title, content }),
    });
    setTitle("");
    setContent("");
    await load();
  }

  async function exportCsv() {
    if (!token) return;
    const csv = await api<string>("/api/history/export?format=csv", { token });
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "qa-history.csv";
    a.click();
  }

  function logout() {
    clearToken();
    router.push("/login");
  }

  if (!dash) return <main className="container">Loading…</main>;

  const usagePct = Math.min(100, Math.round((dash.queries_used / dash.queries_limit) * 100));

  return (
    <main className="container">
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1>{dash.workspace}</h1>
          <p className="muted">
            {dash.email} · plan {dash.plan} · {dash.queries_used}/{dash.queries_limit} queries ({usagePct}%)
          </p>
        </div>
        <button className="btn secondary" onClick={logout}>
          Log out
        </button>
      </header>

      <div className="grid two">
        <section className="card">
          <h2>Documents ({dash.knowledge_entries})</h2>
          <ul>
            {docs.map((d) => (
              <li key={d.id}>
                <strong>{d.title}</strong>{" "}
                <span className={`badge ${d.status}`}>{d.status}</span>
              </li>
            ))}
          </ul>
          <form onSubmit={addDoc}>
            <label>New doc</label>
            <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
            <textarea
              placeholder="Content"
              rows={4}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
            />
            <button className="btn" type="submit">
              Upload (background job)
            </button>
          </form>
        </section>

        <section className="card">
          <h2>Ask</h2>
          <form onSubmit={ask}>
            <textarea
              placeholder="Question about team docs"
              rows={3}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              required
            />
            <button className="btn" type="submit">
              Ask
            </button>
          </form>
          {msg && <p style={{ color: "#f87171" }}>{msg}</p>}
          {answer && (
            <div style={{ marginTop: "1rem" }}>
              <strong>Answer</strong>
              <p>{answer}</p>
            </div>
          )}
        </section>
      </div>

      <section className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2>History</h2>
          <button className="btn secondary" type="button" onClick={exportCsv}>
            Export CSV
          </button>
        </div>
        {history.length === 0 ? (
          <p className="muted">No questions yet.</p>
        ) : (
          <ul>
            {history.slice(0, 8).map((h) => (
              <li key={h.id} style={{ marginBottom: "0.75rem" }}>
                <div>
                  <strong>Q:</strong> {h.question}
                </div>
                <div className="muted">{h.answer.slice(0, 120)}…</div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <Link href="/" className="muted">
        Home
      </Link>
    </main>
  );
}
