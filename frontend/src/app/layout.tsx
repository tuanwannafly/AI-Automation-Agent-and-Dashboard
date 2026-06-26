import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Automation Agent Dashboard',
  description: 'Intelligent task automation with multi-agent workflows',
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