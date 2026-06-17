import { ReportView } from "@/components/report-view";

export default async function ReportPage({
  params,
}: {
  params: Promise<{ chartId: string }>;
}) {
  const { chartId } = await params;

  return (
    <main className="px-4 py-8 sm:px-6 lg:px-10 print:px-0 print:py-0">
      <div className="mx-auto max-w-6xl space-y-6 print:max-w-none">
        <ReportView chartId={chartId} />
      </div>
    </main>
  );
}
