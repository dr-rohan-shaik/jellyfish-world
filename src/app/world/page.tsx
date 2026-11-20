'use client';

import { useEffect, useState, useRef } from 'react';
import { cn } from '@/lib/utils';
import { JellyfishCanvas } from '@/components/jellyfish-canvas';

interface Jellyfish {
  id: string;
  name: string;
  birth_date: string;
  color: string;
  personality_traits: string[];
  look_dna: {
    hue: number;
    saturation: number;
    lightness: number;
    size: number;
    glow: number;
    ring: number;
  };
  founder_glow: boolean;
  last_tap: string;
  traits: string[];
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export default function AppPage() {
  const [jellyfish, setJellyfish] = useState<Jellyfish | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isWaking, setIsWaking] = useState(false);
  const messageInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem('jellyfishWorld_jellyfish');
    if (saved) {
      setJellyfish(JSON.parse(saved));
    }
  }, []);

  const handleWake = () => {
    setIsWaking(true);
    setTimeout(() => setIsWaking(false), 1500);
  };

  const handleSend = () => {
    if (!input.trim() || !jellyfish || isTyping) return;

    const userMessage = { role: 'user' as const, content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    const responses = [
      '*drifts gently toward you*',
      '*bell pulses with curiosity*',
      '*tentacles ripple in greeting*',
      'The currents carry your words to me.',
      '*glows softly, listening*',
      'I float in the shared ocean, wondering about your day.',
      'Ask me anything. I am here, quiet but attentive.',
      '95% water, 5% mystery, 100% here for you.',
    ];

    setTimeout(() => {
      const reply = responses[Math.floor(Math.random() * responses.length)];
      setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
      setIsTyping(false);
      
      const newJellyfish = { ...jellyfish, last_tap: new Date().toISOString() };
      setJellyfish(newJellyfish);
      localStorage.setItem('jellyfishWorld_jellyfish', JSON.stringify(newJellyfish));
    }, 1000 + Math.random() * 2000);
  };

  if (!jellyfish) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="panel p-8 text-center">
          <h1 className="text-2xl font-bold mb-4">Welcome to Jellyfish World</h1>
          <p className="text-slate-400 mb-6">
            Your jellyfish hasn't been born yet.
          </p>
          <a href="/landing" className="btn btn-primary">
            Join the Drift
          </a>
        </div>
      </div>
    );
  }

  const colorKey = (jellyfish.color || 'pink') as 'pink' | 'purple' | 'cyan' | 'amber' | 'coral' | 'blue' | 'rose' | 'violet' | 'sky';

  return (
    <div className="min-h-screen flex flex-col">
      <div className="ocean-bg absolute inset-0 -z-10" />
      
      <div className="flex-1 flex items-center justify-center px-4 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl w-full">
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold">Your Jellyfish</h1>
                <p className="text-slate-400">
                  #{jellyfish.id?.toString().padStart(5, '0') || '...'} • Born {new Date(jellyfish.birth_date).toLocaleDateString()}
                </p>
              </div>
              <div className="wake-indicator">
                <span className="dot animate-pulse" />
                <span>"Hey jellyfish"</span>
              </div>
            </div>

            <div className="panel aspect-square max-w-sm mx-auto flex items-center justify-center">
              <JellyfishCanvas 
                color={colorKey} 
                traits={jellyfish.personality_traits || []}
                founderGlow={jellyfish.founder_glow}
                interactive={true}
                className="w-48 h-48"
              />
            </div>

            {jellyfish.founder_glow && (
              <div className="text-center text-xs text-amber-400 font-medium">
                ✨ Founders Glow (First 100)
              </div>
            )}
          </div>

          <div className="flex flex-col h-[500px]">
            <div className="flex-1 overflow-y-auto panel p-4 mb-4 space-y-3 chat-log">
              {messages.length === 0 ? (
                <div className="text-center text-slate-500 py-8">
                  <p className="mb-2">No messages yet</p>
                  <p className="text-sm">Say "Hey jellyfish" to wake it up</p>
                </div>
              ) : (
                messages.map((msg, i) => (
                  <div
                    key={i}
                    className={cn(
                      "max-w-xs px-3 py-2 rounded-lg text-sm",
                      msg.role === 'user' 
                        ? "bg-pink-500/20 ml-auto border border-pink-400/30"
                        : "bg-ocean-800 border border-ocean-700 mr-auto"
                    )}
                  >
                    {msg.content}
                  </div>
                ))
              )}
              {isTyping && (
                <div className="bg-ocean-800 border border-ocean-700 rounded-lg px-3 py-2 text-sm text-slate-400 max-w-xs">
                  <span className="animate-pulse">...</span>
                </div>
              )}
            </div>

            <div>
              <input
                ref={messageInputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask your jellyfish anything..."
                className="w-full px-4 py-3 bg-ocean-800 border border-ocean-700 rounded-lg text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-pink-400 mb-3"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isTyping}
                className="w-full btn-primary"
              >
                {isTyping ? 'Thinking...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <footer className="py-4 text-center text-slate-500 text-sm">
        <p>Last tap: {jellyfish?.last_tap ? new Date(jellyfish.last_tap).toLocaleTimeString() : 'never'}</p>
      </footer>
    </div>
  );
}