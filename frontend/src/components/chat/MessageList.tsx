import { Message } from "@/types/agent";

interface Props {
  messages: Message[];
}

export function MessageList({ messages }: Props) {
  return (
    <div className="space-y-4">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
        >
          <div
            className={`max-w-[80%] rounded-lg px-4 py-3 ${
              msg.role === "user"
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-gray-100"
            }`}
          >
            <p className="whitespace-pre-wrap">{msg.content}</p>
            {msg.reasoning && msg.reasoning.length > 0 && (
              <details className="mt-2 text-xs text-gray-400">
                <summary className="cursor-pointer hover:text-gray-300">Reasoning ({msg.reasoning.length} steps)</summary>
                <div className="mt-2 space-y-1">
                  {msg.reasoning.map((step, i) => (
                    <div key={i} className="bg-gray-900 rounded p-2">
                      <span className="font-medium">{step.type}:</span> {step.content?.slice(0, 200)}
                    </div>
                  ))}
                </div>
              </details>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}