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
      </div>
    </main>
  );
}