import React, { useEffect, useState } from 'react';

export default function AnalyzingPage() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 2;
      });
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative flex min-h-screen w-full flex-col bg-background-light font-display text-slate-900">
      <header className="flex items-center justify-between border-b border-slate-200 px-6 py-4 md:px-20 lg:px-40 bg-white">
        <div className="flex items-center gap-2">
          <div className="text-primary">
            <span className="material-symbols-outlined text-3xl">psychology</span>
          </div>
          <h2 className="text-slate-900 text-xl font-bold tracking-tight">CogniEase</h2>
        </div>
        <div className="flex items-center gap-4">
          <div className="h-10 w-10 rounded-full bg-slate-200 overflow-hidden border-2 border-primary/20">
            <img alt="Profile" className="h-full w-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuApYUE5AAsAdo5B0O52Q6KF6qpqk_3By4dSGtS1wT6Pwh46hP7z6aUiBZ68wJKGNRFATG-QIKYjnNrVHcfCVi8Rn7QQT9afWLPzI5pO54fikBNw_AB7O84fK2C2Kl5OuiuIch4lkdU012wEN71yyoH1BqlQYUjdMryy3Pmwvr1oA5HcYUuLrPjjNVG5HXmvYOvgoNGwh5a8x-IIWMlZAHGCa8qMw_UpeFguZJVgPKVK6NZoVk3MDwaX1JPHmQ1e8PX65WmfS3aL0Ds" />
          </div>
        </div>
      </header>
      <main className="flex flex-1 flex-col items-center justify-center px-4 py-12">
        <div className="w-full max-w-md flex flex-col items-center">
          <div className="relative flex items-center justify-center mb-8">
            <div className="absolute h-32 w-32 rounded-full border-4 border-primary/20 pulse-animation"></div>
            <div className="relative h-24 w-24 rounded-full border-t-4 border-primary border-r-4 border-r-transparent animate-spin"></div>
            <div className="absolute flex items-center justify-center">
              <span className="material-symbols-outlined text-primary text-4xl">auto_awesome</span>
            </div>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 mb-6 text-center">
            Analysing website…
          </h1>
          <div className="w-full bg-white rounded-xl p-6 shadow-sm border border-slate-100 mb-8">
            <div className="flex justify-between items-end mb-2">
              <span className="text-sm font-medium text-slate-600 uppercase tracking-wider">Current Task</span>
              <span className="text-primary font-bold">{progress}%</span>
            </div>
            <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full transition-all duration-75" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
          <div className="flex flex-col gap-4 w-full text-center">
            <div className="flex items-center justify-center gap-3 text-slate-900 font-medium py-2 px-4 rounded-lg bg-primary/10 border border-primary/20">
              <span className="material-symbols-outlined text-primary text-xl">web_asset</span>
              <p>Evaluating layout density</p>
            </div>
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-center gap-2 text-slate-400 text-sm">
                <span className="material-symbols-outlined text-base">check_circle</span>
                <p>Extracting webpage content</p>
              </div>
              <div className="flex items-center justify-center gap-2 text-slate-400 text-sm">
                <span className="material-symbols-outlined text-base">check_circle</span>
                <p>Analysing language complexity</p>
              </div>
              <div className="flex items-center justify-center gap-2 text-slate-300 text-sm">
                <span className="material-symbols-outlined text-base">pending</span>
                <p>Calculating cognitive accessibility score</p>
              </div>
            </div>
          </div>
        </div>
      </main>
      <footer className="py-10 px-6 flex justify-center border-t border-slate-200 bg-white">
        <div className="flex gap-12 text-center">
          <div>
            <p className="text-xs text-slate-500 uppercase font-semibold">Nodes Scanned</p>
            <p className="text-xl font-bold text-slate-900">1,248</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase font-semibold">Contrast Points</p>
            <p className="text-xl font-bold text-slate-900">84</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase font-semibold">Readability</p>
            <p className="text-xl font-bold text-slate-900">WCAG 2.1</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
