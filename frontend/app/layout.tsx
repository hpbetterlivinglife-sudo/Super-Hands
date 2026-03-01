import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Super Hands OS",
  description: "Autonomous Agent Command Center",
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
