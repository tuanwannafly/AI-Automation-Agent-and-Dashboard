'use client';

import { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface InputAreaProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function InputArea({ onSend, disabled = false }: InputAreaProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    console.log('[InputArea] handleSend called, input:', input, 'disabled:', disabled);
    if (input.trim() && !disabled) {
      console.log('[InputArea] Calling onSend with:', input.trim());
      onSend(input.trim());
      setInput('');
    } else {
      console.log('[InputArea] Not sending: input empty or disabled');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-700 p-4 bg-gray-800">
      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message... (Enter to send, Shift+Enter for new line)"
          className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
          rows={3}
          disabled={disabled}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || disabled}
          className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center justify-center"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}