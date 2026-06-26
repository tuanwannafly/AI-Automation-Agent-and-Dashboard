export default function HomePage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">AI Automation Agent</h1>
        <p className="text-gray-400 mb-8">Intelligent task automation with multi-agent workflows</p>
        <div className="flex gap-4 justify-center">
          <a href="/chat" className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors">
            Open Chat
          </a>
          <a href="/workflows" className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors">
            Browse Workflows
          </a>
        </div>
      </div>
    </div>
  );
}