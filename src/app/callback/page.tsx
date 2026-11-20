export const metadata = {
  title: 'Magic Link Sent',
  description: 'Check your email',
};

export default function CallbackPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="panel p-8 text-center">
        <h1 className="text-2xl font-bold mb-4">Welcome to Jellyfish World</h1>
        <p className="text-slate-400 mb-6">
          You've been redirected here by your magic link.
        </p>
        <p className="text-slate-500">
          Please check your email or visit the main app.
        </p>
      </div>
    </div>
  );
}