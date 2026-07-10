export default function Tutorial() {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-700/60 px-8 py-5">
        <h1 className="text-2xl font-semibold text-white">Tutorial</h1>
        <p className="mt-1 text-sm text-slate-400">
          Deep-dive documentation: every service, failure modes, production tradeoffs, and
          interview talking points
        </p>
      </div>
      <iframe
        src="/api/v1/tutorial"
        title="Platform Tutorial"
        className="w-full flex-1 border-0 bg-white"
      />
    </div>
  );
}
