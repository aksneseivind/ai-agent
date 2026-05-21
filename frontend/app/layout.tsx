import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI CV Agent",
  description: "AI-powered CV assistant",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}