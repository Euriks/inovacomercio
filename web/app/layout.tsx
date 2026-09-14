import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InovaComércio MS · NFC-e Offline",
  description: "Demonstração de contingência offline NFC-e para o varejo de proximidade em Mato Grosso do Sul.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
