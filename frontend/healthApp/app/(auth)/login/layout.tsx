import "@/styles/globals.css";
import { Providers } from "@/app/providers";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div>
      <Providers themeProps={{ attribute: "class", defaultTheme: "dark" }}>
        {children}
      </Providers>
    </div>
  );
}