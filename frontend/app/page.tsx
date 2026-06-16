import Link from "next/link";

const experienceCards = [
  {
    title: "Temporary Chart Sessions",
    body: "Birth details now create a short-lived chart ID instead of keeping everything in one page state.",
  },
  {
    title: "Chart Dashboard",
    body: "The dashboard shape now separates chart facts, cusp tables, dasha timing, and future reasoning layers.",
  },
  {
    title: "Question Workspace",
    body: "Questions are asked against a chart session so we can evolve toward topic mapping, significators, and timing logic.",
  },
];

const productPrinciples = [
  "No login for MVP, but do not expose private birth details in public URLs.",
  "Keep calculation logic separate from API routes and keep interpretation logic separate from raw chart facts.",
  "Label all astrology output as interpretive and placeholder-based until the real KP engine is integrated.",
];

export default function HomePage() {
  return (
    <main className="relative overflow-hidden px-4 py-8 text-midnight sm:px-6 lg:px-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-8">
        <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="glass-panel bg-orbital-grid p-8 sm:p-10">
            <p className="section-title">KP Astrology Q&A MVP</p>
            <h1 className="mt-4 max-w-3xl font-[family-name:var(--font-heading)] text-5xl font-semibold leading-none text-midnight sm:text-6xl">
              Grow this into a real KP chart and question workflow.
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-midnight/75 sm:text-lg">
              The app now moves beyond a single demo form and starts matching your larger product prompt:
              temporary chart sessions, dedicated chart dashboards, question workspaces, and a cleaner path
              toward real KP methodology modules.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/birth-details"
                className="rounded-full bg-midnight px-6 py-3 text-sm font-semibold text-white transition hover:bg-aurora"
              >
                Start Birth Details
              </Link>
              <Link
                href="/methodology"
                className="rounded-full border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-midnight transition hover:border-aurora hover:text-aurora"
              >
                View Methodology
              </Link>
            </div>
          </div>

          <aside className="glass-panel p-6 sm:p-8">
            <p className="section-title">Build Direction</p>
            <h2 className="mt-3 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
              This is now a phase-two scaffold.
            </h2>
            <p className="mt-4 text-sm leading-7 text-midnight/70">
              The architecture is being prepared for geocoding, timezone resolution, dasha timing, curated
              KP knowledge rules, and more careful disclaimers without over-claiming astrology accuracy.
            </p>
            <dl className="mt-6 grid gap-4 text-sm">
              {productPrinciples.map((item) => (
                <div key={item} className="rounded-2xl bg-slate-50 p-4">
                  <dd className="text-midnight/70">{item}</dd>
                </div>
              ))}
            </dl>
          </aside>
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          {experienceCards.map((card) => (
            <div key={card.title} className="glass-panel p-6 sm:p-8">
              <p className="section-title">{card.title}</p>
              <p className="mt-4 text-sm leading-7 text-midnight/70">{card.body}</p>
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}
