'use client';

import { ChatInterface } from '@/components/chat/ChatInterface';
import { AgentPanel } from '@/components/agent/AgentPanel';
import { LLMSwitcher } from '@/components/ui/LLMSwitcher';
import { FileUploadZone } from '@/components/upload/FileUploadZone';
import { UploadedFileList } from '@/components/upload/UploadedFileList';
import { useState } from 'react';

export default function ChatInterfacePage() {
  const [agentPanelOpen, setAgentPanelOpen] = useState(true);

  return (
    <div className="flex h-screen bg-gray-900">
      <div className="flex-1 flex flex-col">
        <header className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gray-800">
          <h1 className="text-xl font-bold text-white">AI Chat</h1>
          <div className="flex items-center gap-4">
            <LLMSwitcher />
          </div>
        </header>
        <main className="flex-1 flex overflow-hidden">
          <div className="flex-1 flex flex-col">
            <ChatInterface />
            <div className="border-t border-gray-700 p-4 bg-gray-800">
              <FileUploadZone />
              <UploadedFileList />
            </div>
          </div>
          <AgentPanel isOpen={agentPanelOpen} onToggle={() => setAgentPanelOpen(!agentPanelOpen)} />
        </main>
      </div>
    </div>
  );
}