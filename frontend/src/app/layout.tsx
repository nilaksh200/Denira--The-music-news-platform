import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Denira Desktop — Inshorts Music News & Editorial Deck',
  description:
    'Curated, high-signal music news and editorial card deck engineered exclusively for desktop browsers. Updated every 6 hours.',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-neutral-950 text-white min-h-screen overflow-hidden antialiased">
        {children}
      </body>
    </html>
  );
}
