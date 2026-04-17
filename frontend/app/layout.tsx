import type { Metadata, Viewport } from "next";
import "./globals.css";
import { MatrixRain } from "@/components/MatrixRain";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Realitní Asistent",
  description: "Osobní AI asistent pro realitního makléře",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "Realitní Asistent",
  },
  icons: {
    icon: "/icons/icon.svg",
    apple: "/icons/icon.svg",
  },
};

export const viewport: Viewport = {
  themeColor: "#000000",
  width: "device-width",
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
    <html lang="cs" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var t = localStorage.getItem('theme') || 'matrix';
                  if (t === 'readable') document.documentElement.classList.add('readable');
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body>
        <MatrixRain />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
