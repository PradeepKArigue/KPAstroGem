import { ChartDashboard } from "@/components/chart-dashboard";

export default async function DashboardPage({
  params,
}: {
  params: Promise<{ chartId: string }>;
}) {
  const { chartId } = await params;

  return (
    <main className="px-4 py-8 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <ChartDashboard chartId={chartId} />
      </div>
    </main>
  );
}

