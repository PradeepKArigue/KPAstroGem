import { BirthForm } from "@/components/birth-form";

export default function BirthDetailsPage() {
  return (
    <main className="px-4 py-8 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="glass-panel bg-orbital-grid p-8 sm:p-10">
          <p className="section-title">Birth Session Setup</p>
          <h1 className="mt-3 font-[family-name:var(--font-heading)] text-5xl font-semibold text-midnight">
            Capture birth details without creating an account
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-7 text-midnight/75">
            This phase introduces the chart-session model from your larger product prompt. The form now
            collects timezone, state, and optional manual coordinates so the backend can return a
            short-lived chart ID and a more scalable placeholder KP structure.
          </p>
        </section>

        <BirthForm />
      </div>
    </main>
  );
}

