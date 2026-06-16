import { QuestionWorkspace } from "@/components/question-workspace";

export default async function AskPage({
  params,
}: {
  params: Promise<{ chartId: string }>;
}) {
  const { chartId } = await params;

  return (
    <main className="px-4 py-8 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <QuestionWorkspace chartId={chartId} />
      </div>
    </main>
  );
}

