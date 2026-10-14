import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Fulfillment Exception Dashboard',
  description: 'Operations dashboard for fulfillment exception investigation and approvals.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
