import { baseUrl, createMetadata } from "@/lib/metadata";
import { RootProvider } from 'fumadocs-ui/provider/next';
import './global.css';
import { Inter } from 'next/font/google';

export const metadata = createMetadata({
  title: {
    template: "%s | Fresh",
    default: "Fresh",
  },
  metadataBase: baseUrl,
});


const inter = Inter({
  subsets: ['latin'],
});

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <body className="flex flex-col min-h-screen">
        <RootProvider>{children}</RootProvider>
      </body>
    </html>
  );
}
