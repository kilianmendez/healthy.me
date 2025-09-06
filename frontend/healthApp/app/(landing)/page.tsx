import { Link } from "@heroui/link";
import { Snippet } from "@heroui/snippet";
import { Code } from "@heroui/code";
import { button as buttonStyles } from "@heroui/theme";
import { Button } from "@/components/ui/button"

import { siteConfig } from "@/config/site";
import { title, subtitle } from "@/components/primitives";
import { GithubIcon } from "@/components/icons";

export default function Home() {
  return (
    <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
      <Button className="mt-4" variant="default" size="lg">
          <Link
            href="/login"
            className="flex items-center gap-2 text-primary-foreground"
          >
            Login
          </Link>
      </Button>
      <Button className="mt-4" variant="secondary" size="lg">
          <Link
            href="/register"
            className="flex items-center gap-2"
          >
            Register
          </Link>
      </Button>
    </section>
  );
}
