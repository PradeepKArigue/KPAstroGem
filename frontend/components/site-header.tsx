import Link from "next/link";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/birth-details", label: "New Chart" },
  { href: "/methodology", label: "KP Method" },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20">
      <div className="mx-auto flex max-w-7xl items-center justify-between rounded-full border border-white/60 bg-white/75 px-5 py-3 shadow-halo backdrop-blur sm:px-6">
        <Link href="/" className="font-[family-name:var(--font-heading)] text-2xl font-semibold text-midnight">
          KPAstroGem
        </Link>
        <nav className="flex items-center gap-2 sm:gap-3">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-full px-4 py-2 text-sm font-semibold text-midnight/75 transition hover:bg-slate-100 hover:text-midnight"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

