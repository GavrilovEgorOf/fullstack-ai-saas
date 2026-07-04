import Link from "next/link";

export default function HomePage() {
  return (
    <main className="container">
      <h1>Team Knowledge</h1>
      <p className="muted">
        Shared doc library for your team. Upload notes, ask questions, get answers with sources.
      </p>
      <div className="card">
        <h2>What you get</h2>
        <ul>
          <li>Workspace login and usage limits (free vs pro)</li>
          <li>Doc upload with background indexing</li>
          <li>Q&A with citations and exportable history</li>
          <li>FastAPI backend + Next.js dashboard</li>
        </ul>
      </div>
      <Link className="btn" href="/login">
        Sign in
      </Link>
    </main>
  );
}
