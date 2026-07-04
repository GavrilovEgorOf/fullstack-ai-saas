import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Team Knowledge",
  description: "Team doc library with AI Q&A",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
