'use client';

interface StreamingTextProps {
  content: string;
}

export function StreamingText({ content }: StreamingTextProps) {
  return (
    <div className="whitespace-pre-wrap">{content}</div>
  );
}