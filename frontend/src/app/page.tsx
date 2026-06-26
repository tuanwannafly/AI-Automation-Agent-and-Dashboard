"use client";

export default function Home() {
  return (
    <main className="flex min-h-screen">
      <div className="flex flex-col flex-1">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
          <h1 className="font-semibold text-lg tracking-tight">AI Agent Dashboard</h1>
          <span className="text-xs text-gray-500">Phase 5 - Coming Soon</span>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <p className="text-gray-400">Full chat interface will be available after Phase 5 implementation.</p>
        </div>
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold mb-4">AI Agent Dashboard</h1>
      <p className="text-gray-400 text-center max-w-2xl">
        Coming soon - Phase 5 implementation in progress.
        <br />
        This dashboard will provide real-time AI agent interaction with
        chain-of-thought visualization.
      </p>
      <div className="mt-8 p-4 bg-gray-900 rounded-lg">
        <p className="text-sm text-gray-500">
          API: <a href="http://localhost:8000/docs" className="text-blue-400 hover:underline">http://localhost:8000/docs</a>
        </p>
      </div>
    </main>
  );
}