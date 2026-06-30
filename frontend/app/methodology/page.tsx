const publicPatterns = [
  "AstroSage's public home page exposes KP-focused entry points such as What is KP System?, Make KP Chart Online, Ruling Planets Now, KP Panchang Now, KP Horary Chart Online, and a KP tutorial hub.",
  "Its public kundli flow also surfaces advanced birth inputs like longitude, latitude, time zone, DST correction, ayanamsa choice, chart style, and KP horary number.",
  "The broader report family is organized into reusable modules such as dasha analysis, transit-style reports, yearly analysis, and specialized diagnostic reports.",
];

const kpWorkflow = [
  ["1. Normalize birth data", "Resolve birthplace, latitude, longitude, timezone, and historical UTC conversion before chart work begins."],
  ["2. Build cusp framework", "KP reasoning depends heavily on house cusps, their star lords, and their sub lords rather than only on zodiac sign descriptions."],
  ["3. Map planets to houses", "Every planet is read through occupation, ownership, star-lord connection, and sub-lord connection."],
  ["4. Rank significators", "For a life topic such as career or marriage, the engine should highlight supporting, delaying, and opposing houses."],
  ["5. Check dasha timing", "Vimshottari dasha, bhukti, and antara should explain when a promised event becomes more or less active."],
  ["6. Answer by topic", "Each user question should map to a house set, then cite the cusp and significator logic used in the answer."],
  ["7. Show the trail", "The app should make the logic visible so users understand why a result was produced, not just what was produced."],
];

const foundationDone = [
  "Worldwide place lookup and timezone confirmation are already in the chart-entry flow.",
  "Temporary chart sessions keep birth details out of shareable URLs.",
  "The report now includes identity verification, planet tables, cusp tables, a derived significator matrix, a house-activation matrix, and a dasha ladder.",
  "Question sessions already preserve conversation history and expose a calculation trail in the answer workspace.",
];

const nextBuildStages = [
  "Add true advanced KP birth settings across the stack: ayanamsa selection, DST correction controls, chart style preference, and optional KP horary number.",
  "Deepen the automated KP interpretation layer so significator ranking, event promise, and timing logic move closer to practitioner-style reading depth.",
  "Store curated KP rules and house mappings so answers come from repeatable logic rather than broad generic narratives.",
  "Generate a proper server-side PDF report with stable pagination and export-ready tables.",
  "Introduce more KP utilities inspired by the public product landscape: ruling planets, transit overlays, and richer timing drill-downs.",
];

const guardrails = [
  "KP astrology is presented here as a traditional interpretive system, not a scientific guarantee.",
  "Health, legal, finance, and high-stakes topics must stay clearly labeled as cautionary and interpretive.",
  "Astronomical values are now computed, but automated interpretation still needs continued KP validation and refinement.",
];

export default function MethodologyPage() {
  return (
    <main className="px-4 py-8 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="glass-panel bg-orbital-grid p-8 sm:p-10">
          <p className="section-title">Methodology</p>
          <h1 className="mt-3 font-[family-name:var(--font-heading)] text-5xl font-semibold text-midnight">
            Building toward a complete KP workflow
          </h1>
          <p className="mt-5 max-w-4xl text-base leading-7 text-midnight/75">
            As of June 28, 2026, the product direction is to move this app closer to the public KP-style
            experience users recognize from sites such as AstroSage, while keeping the implementation honest:
            real KP calculation layers now, deeper verified interpretation layers next.
          </p>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="glass-panel p-6 sm:p-8">
            <p className="section-title">Public Product Patterns</p>
            <div className="mt-5 space-y-3">
              {publicPatterns.map((item) => (
                <div key={item} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-7 text-midnight/70">
                  {item}
                </div>
              ))}
            </div>
            <p className="mt-5 text-sm leading-7 text-midnight/65">
              These are public observations from the AstroSage home page structure, used as product inspiration
              only rather than copied proprietary content.
            </p>
          </div>

          <div className="glass-panel p-6 sm:p-8">
            <p className="section-title">Current Guardrails</p>
            <div className="mt-5 space-y-3">
              {guardrails.map((item) => (
                <div key={item} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-7 text-midnight/70">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="glass-panel p-6 sm:p-8">
          <p className="section-title">KP Reading Sequence</p>
          <div className="mt-5 grid gap-3 lg:grid-cols-2">
            {kpWorkflow.map(([title, detail]) => (
              <div key={title} className="rounded-2xl bg-slate-50 px-4 py-4">
                <p className="text-sm font-semibold text-midnight">{title}</p>
                <p className="mt-2 text-sm leading-7 text-midnight/70">{detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="glass-panel p-6 sm:p-8">
            <p className="section-title">Foundation Already Shipped</p>
            <div className="mt-5 space-y-3">
              {foundationDone.map((item) => (
                <div key={item} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-7 text-midnight/70">
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="glass-panel p-6 sm:p-8">
            <p className="section-title">Next Build Stages</p>
            <div className="mt-5 space-y-3">
              {nextBuildStages.map((item) => (
                <div key={item} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-7 text-midnight/70">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
