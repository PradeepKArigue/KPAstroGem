const principles = [
  "KP astrology is presented here as a traditional interpretive system, not a scientific guarantee.",
  "Future versions will separate calculation facts, KP interpretation, assumptions, confidence, and disclaimers more deeply.",
  "Birth time precision matters because cusp sub lords and event timing are highly sensitive in KP methodology.",
  "This MVP keeps all astrology outputs placeholder-based until the actual chart engine, house logic, and dasha calculations are integrated.",
];

const roadmap = [
  "Integrate a proper ephemeris abstraction layer and timezone-aware birth normalization.",
  "Add real cusp, star-lord, sub-lord, and dasha calculations.",
  "Introduce curated KP rules, question-house mappings, and explanation templates.",
  "Add temporary report generation and a richer calculation trail.",
];

export default function MethodologyPage() {
  return (
    <main className="px-4 py-8 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="glass-panel bg-orbital-grid p-8 sm:p-10">
          <p className="section-title">Methodology</p>
          <h1 className="mt-3 font-[family-name:var(--font-heading)] text-5xl font-semibold text-midnight">
            How this KP app is being shaped
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-7 text-midnight/75">
            The product direction is now aligned with a dedicated KP Q&A application rather than a generic
            astrology demo. This page makes the current limitations explicit while preparing the future
            architecture for chart sessions, question workflows, and rule-based interpretation.
          </p>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="glass-panel p-6 sm:p-8">
            <p className="section-title">Current Principles</p>
            <div className="mt-5 space-y-3">
              {principles.map((item) => (
                <div key={item} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-7 text-midnight/70">
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="glass-panel p-6 sm:p-8">
            <p className="section-title">Next Technical Steps</p>
            <div className="mt-5 space-y-3">
              {roadmap.map((item) => (
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

