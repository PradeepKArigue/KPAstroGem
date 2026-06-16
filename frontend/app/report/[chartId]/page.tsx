import Link from "next/link";

export default async function ReportPage({
  params,
}: {
  params: Promise<{ chartId: string }>;
}) {
  const { chartId } = await params;

  return (
    <main className="px-4 py-8 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-5xl space-y-6">
        <section className="glass-panel bg-orbital-grid p-8 sm:p-10">
          <p className="section-title">Report Placeholder</p>
          <h1 className="mt-3 font-[family-name:var(--font-heading)] text-5xl font-semibold text-midnight">
            Full report flow is reserved for the next phase
          </h1>
          <p className="mt-5 text-base leading-7 text-midnight/75">
            Chart ID: {chartId}. This route is intentionally in place so the app structure can grow toward
            downloadable reports, question history, and a calculation trail without another URL redesign.
          </p>
          <div className="mt-6">
            <Link href={`/dashboard/${chartId}`} className="rounded-full bg-midnight px-6 py-3 text-sm font-semibold text-white transition hover:bg-aurora">
              Back to dashboard
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
