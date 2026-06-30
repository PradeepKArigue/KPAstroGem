import Link from "next/link";

const experienceCards = [
  {
    title: "Structured Chart Sessions",
    body: "Each consultation starts with a reusable chart session so birth details, report data, and question history stay connected.",
  },
  {
    title: "Report-Ready KP Tables",
    body: "Planetary positions, cusp structures, dasha layers, and chart interpretation are organized into cleaner KP-oriented sections.",
  },
  {
    title: "Interactive Guidance",
    body: "Follow-up questions stay attached to the same chart session so the reading feels continuous instead of disconnected.",
  },
];

const productPrinciples = [
  "Keep private birth details out of shareable URLs while still allowing a smooth chart workflow.",
  "Separate chart computation, location validation, and interpretation layers so the product can evolve safely.",
  "Favor clear confidence signals, traceable logic, and readable reports over vague or over-claimed output.",
];

export default function HomePage() {
  return (
    <main className="relative overflow-hidden px-4 py-8 text-midnight sm:px-6 lg:px-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-8">
        <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="glass-panel bg-orbital-grid p-8 sm:p-10">
            <p className="section-title">Professional KP Workflow</p>
            <h1 className="mt-4 max-w-3xl font-[family-name:var(--font-heading)] text-5xl font-semibold leading-none text-midnight sm:text-6xl">
              Build accurate chart sessions, readable reports, and confident follow-up guidance.
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-midnight/75 sm:text-lg">
              KPAstroGem is designed as a complete consultation flow: capture birth details, confirm the
              resolved location, generate a structured chart report, and continue the same reading through
              contextual question answering.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/birth-details"
                className="rounded-full bg-midnight px-6 py-3 text-sm font-semibold text-white transition hover:bg-aurora"
              >
                Start New Chart
              </Link>
              <Link
                href="/methodology"
                className="rounded-full border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-midnight transition hover:border-aurora hover:text-aurora"
              >
                Review KP Method
              </Link>
            </div>
          </div>

          <aside className="glass-panel p-6 sm:p-8">
            <p className="section-title">Product Direction</p>
            <h2 className="mt-3 font-[family-name:var(--font-heading)] text-3xl font-semibold text-midnight">
              A consultation flow that feels usable from the first screen.
            </h2>
            <p className="mt-4 text-sm leading-7 text-midnight/70">
              The application is being shaped around reliable place resolution, session-based charts,
              structured KP reporting, and a question workspace that can grow into deeper analysis without
              losing traceability.
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
