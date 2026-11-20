export const metadata = {
  title: 'Jellyfish World',
  description: 'One AI jellyfish per verified email. Floating in the shared ocean, answering when called.',
};

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="panel p-8 text-center">
        <h1 className="text-2xl font-bold mb-4">Welcome to Jellyfish World</h1>
        <p className="text-slate-400 mb-6">
          One AI jellyfish per verified email. Floating in the shared ocean, answering when called.
        </p>
        <a href="/landing" className="btn btn-primary">
          Join the Drift
        </a>
      </div>
    </div>
  );
}