import { BirthForm } from "@/components/birth-form";

export default function BirthDetailsPage() {
  return (
    <main className="px-4 py-8 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="glass-panel bg-orbital-grid p-8 sm:p-10">
          <p className="section-title">Birth Session Setup</p>
          <h1 className="mt-3 font-[family-name:var(--font-heading)] text-5xl font-semibold text-midnight">
            Start a chart with precise birth, place, and timezone details
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-7 text-midnight/75">
            Enter the birth identity once, confirm the resolved location, and continue into a reusable
            chart session. The app uses city search, state and country context, timezone resolution, and
            optional manual coordinate overrides when you need tighter control.
          </p>
        </section>

        <BirthForm />
      </div>
    </main>
  );
}

