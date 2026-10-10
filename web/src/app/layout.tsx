import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Quantum Crop Intelligence",
  description: "Agricultural crop suitability analysis.",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Let language be set dynamically later, default to en
  return (
    <html lang="en" className={`${inter.variable}`}>
      <body>
        {children}
      </body>
    </html>
  );
}
