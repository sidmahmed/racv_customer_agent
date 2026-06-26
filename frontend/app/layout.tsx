import type { Metadata } from "next";
import { Inter, Poppins } from "next/font/google";
import "./globals.css";

// RACV Modern design system (DESIGN.md) specifies Poppins for headings/labels
// and "Suisse Intl" for body copy. Suisse Intl is a licensed font we don't
// have rights to embed, so Inter (a similar free neutral grotesque) is loaded
// as the practical stand-in -- "Suisse Intl" is still listed first in the
// font stack in case it's ever self-hosted or present on the user's system.
const poppins = Poppins({
  variable: "--font-poppins",
  subsets: ["latin"],
  weight: ["400", "500"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "RACV Help Assistant",
  description: "Ask about RACV roadside assistance, insurance, billing, and more.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${poppins.variable} ${inter.variable} h-full antialiased`}>
      <body className="h-full flex flex-col overflow-hidden">{children}</body>
    </html>
  );
}
