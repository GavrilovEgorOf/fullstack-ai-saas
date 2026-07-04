const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8020";

export type AuthResponse = {
  access_token: string;
  workspace: string;
  plan: string;
};

export async function api<T>(
  path: string,
  options: RequestInit & { token?: string } = {}
): Promise<T> {
  const { token, ...init } = options;
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(init.headers || {}),
  };
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API}${path}`, { ...init, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("text/csv")) {
    return (await res.text()) as T;
  }
  return res.json() as Promise<T>;
}

export function saveToken(token: string) {
  if (typeof window !== "undefined") localStorage.setItem("tk_token", token);
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("tk_token");
}

export function clearToken() {
  if (typeof window !== "undefined") localStorage.removeItem("tk_token");
}
