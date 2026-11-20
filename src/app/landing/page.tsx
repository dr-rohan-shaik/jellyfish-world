'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { JellyfishCanvas } from '@/components/jellyfish-canvas';

export default function LandingPage() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="min-h-screen flex flex-col">
      <div className="ocean-bg absolute inset-0 -z-10" />
      
      <div className="flex-1 flex flex-col items-center justify-center px-4 relative z-10">
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-pink-300 via-purple-300 to-cyan-300">
            Jellyfish World
          </h1>
          <p className="text-xl text-slate-400 max-w-md mx-auto">
            One AI jellyfish per verified email. Floating in the shared ocean, answering when called.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div className="space-y-6">
            <div className="panel p-8">
              <h2 className="text-2xl font-semibold mb-4">Join the Drift</h2>
              <p className="text-slate-400 mb-6">Enter your email to get a magic link. No ads, no pressure.</p>
              
              <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-ocean-800 border border-ocean-700 rounded-lg text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-pink-400"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Your Jellyfish Name
                  </label>
                  <input
                    type="text"
                    placeholder="Aurora, Lumina, Drift..."
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    maxLength={20}
                    className="w-full px-4 py-3 bg-ocean-800 border border-ocean-700 rounded-lg text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-pink-400"
                  />
                  <p className="text-xs text-slate-500 mt-1">20 characters max</p>
                </div>
                <button
                  type="submit"
                  disabled={isLoading || !email}
                  className="w-full btn-primary"
                >
                  {isLoading ? 'Sending magic link...' : 'Get My Jellyfish'}
                </button>
              </form>
            </div>

            <div className="panel p-6">
              <h3 className="font-medium mb-3">How it works</h3>
              <ul className="text-sm text-slate-400 space-y-2">
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-pink-400 rounded-full" />
                  Verify your email with a magic link
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-pink-400 rounded-full" />
                  Your jellyfish is born with a unique number
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-pink-400 rounded-full" />
                  Ask it anything with "Hey jellyfish"
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-pink-400 rounded-full" />
                  No guilt mechanics, no pressure
                </li>
              </ul>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -top-10 -left-10 w-80 h-80 rounded-full bg-pink-500/20 filter blur-3xl animate-pulse" />
            <div className="absolute -bottom-10 -right-10 w-80 h-80 rounded-full bg-cyan-500/20 filter blur-3xl animate-pulse" style={{ animationDelay: '0.5s' }} />
            
            <div className="panel relative overflow-hidden">
              <div className="absolute top-4 right-4">
                <div className="wake-indicator">
                  <span className="dot animate-pulse" />
                  <span>"Hey jellyfish"</span>
                </div>
              </div>
              
              <JellyfishCanvas color="pink" founderGlow={false} interactive={false} />
            </div>
          </div>
        </div>
      </div>

      <footer className="py-8 text-center text-slate-500">
        <p className="text-sm">One jellyfish per verified email. The world is shared.</p>
      </footer>
    </div>
  );
}