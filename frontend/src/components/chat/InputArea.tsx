"use client";

import { useState, useRef } from "react";

interface Props {
  onSend: (text: string, fileIds: string[]) => void;
  disabled: boolean;
}

export function InputArea({ onSend, disabled }: Props) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim() && !disabled) {
      onSend(text, []);
      setText("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-800 p-4">
      <div className="flex gap-2">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Type your message..."
          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 resize-none focus:outline-none focus:border-blue-500 disabled:opacity-50"
          rows={3}
        />
        <button
          type="submit"
          disabled={disabled || !text.trim()}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
        >
          Send
        </button>
      </div>
    </form>
  );
}