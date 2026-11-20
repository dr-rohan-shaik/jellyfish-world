import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Jellyfish World",
  description: "One AI jellyfish per verified email. Floating in the shared ocean, answering when called.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        {children}
      </body>
    </html>
  );
}