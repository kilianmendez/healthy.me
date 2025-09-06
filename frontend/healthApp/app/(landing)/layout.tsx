import "@/styles/globals.css";
import { Navbar } from "@/components/navbar";

export default function LandingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex flex-col h-screen">
      <Navbar />
      <main className="container mx-auto max-w-7xl pt-16 px-6 flex-grow">
        {children}
      </main>
      <footer className="w-full flex items-center justify-center py-3">
        <a
          href="https://heroui.com?utm_source=next-app-template"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-current"
          title="heroui.com homepage"
        >
          <span className="text-default-600">Powered by</span>
          <p className="text-primary">HeroUI</p>
        </a>
      </footer>
    </div>
  );
}
