import React from 'react';

export default function LandingPage({ onCheck }: { onCheck: () => void }) {
  return (
    <div className="relative flex min-h-screen flex-col overflow-x-hidden bg-background-light font-display text-slate-900">
      <div className="layout-container flex h-full grow flex-col">
        <header className="flex items-center justify-between border-b border-primary/10 px-6 py-4 lg:px-20">
          <div className="flex items-center gap-3">
            <div className="text-primary">
              <span className="material-symbols-outlined text-3xl font-bold">psychology</span>
            </div>
            <h2 className="text-xl font-bold tracking-tight">CogniEase</h2>
          </div>
          <div className="flex items-center gap-6">
            <nav className="hidden md:flex items-center gap-8">
              <a className="text-sm font-medium hover:text-primary transition-colors" href="#">Features</a>
              <a className="text-sm font-medium hover:text-primary transition-colors" href="#">Pricing</a>
              <a className="text-sm font-medium hover:text-primary transition-colors" href="#">Resources</a>
            </nav>
            <button className="bg-primary hover:bg-primary/90 text-white text-sm font-bold h-10 px-6 rounded-lg transition-all shadow-md shadow-primary/20 cursor-pointer">
              Sign Up
            </button>
          </div>
        </header>
        <main className="flex-1">
          <section className="relative flex flex-col items-center justify-center px-6 py-20 text-center lg:py-32">
            <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_50%_50%,_var(--tw-gradient-stops))] from-primary/5 via-transparent to-transparent"></div>
            <div className="max-w-3xl flex flex-col gap-6">
              <h1 className="text-5xl font-black tracking-tight lg:text-7xl">
                CogniEase
              </h1>
              <p className="text-xl font-semibold text-primary lg:text-2xl">
                Making the web easier for the human mind
              </p>
              <p className="text-slate-600 text-lg max-w-xl mx-auto">
                Analyze the cognitive accessibility of any webpage in seconds. Identify barriers and improve inclusivity.
              </p>
            </div>
            <div className="mt-12 w-full max-w-2xl">
              <div className="flex flex-col md:flex-row gap-3 p-2 bg-white rounded-xl shadow-xl border border-primary/10">
                <div className="flex flex-1 items-center px-4 gap-3">
                  <span className="material-symbols-outlined text-slate-400">link</span>
                  <input className="w-full bg-transparent border-none focus:ring-0 text-slate-900 placeholder:text-slate-400 py-3 outline-none" placeholder="Enter website URL (e.g. https://example.com)" type="text" />
                </div>
                <button onClick={onCheck} className="bg-gradient-to-r from-primary to-blue-400 hover:brightness-110 text-white font-bold px-8 py-3 rounded-lg transition-all shadow-lg shadow-primary/30 flex items-center justify-center gap-2 cursor-pointer">
                  <span>Check Website</span>
                  <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </button>
              </div>
            </div>
          </section>
          <section className="max-w-7xl mx-auto px-6 py-20">
            <div className="flex flex-col gap-4 text-center mb-16">
              <h2 className="text-3xl font-bold tracking-tight lg:text-4xl">Why Cognitive Accessibility Matters</h2>
              <p className="text-slate-600 max-w-2xl mx-auto">
                Universal design isn't just about physical or visual impairments—it's about how the brain processes information.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="flex flex-col gap-4 p-8 rounded-2xl bg-white border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                <div className="size-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                  <span className="material-symbols-outlined text-3xl">visibility</span>
                </div>
                <h3 className="text-xl font-bold">Clarity</h3>
                <p className="text-slate-600 leading-relaxed">
                  Ensure content is easy to read and understand. We analyze reading levels and visual hierarchy.
                </p>
              </div>
              <div className="flex flex-col gap-4 p-8 rounded-2xl bg-white border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                <div className="size-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                  <span className="material-symbols-outlined text-3xl">gesture</span>
                </div>
                <h3 className="text-xl font-bold">Predictability</h3>
                <p className="text-slate-600 leading-relaxed">
                  Consistent navigation and functional patterns help users with memory or attention challenges.
                </p>
              </div>
              <div className="flex flex-col gap-4 p-8 rounded-2xl bg-white border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                <div className="size-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                  <span className="material-symbols-outlined text-3xl">center_focus_strong</span>
                </div>
                <h3 className="text-xl font-bold">Focus</h3>
                <p className="text-slate-600 leading-relaxed">
                  Minimize distractions and cognitive load to help users stay on task without getting overwhelmed.
                </p>
              </div>
            </div>
          </section>
          <section className="bg-primary/5 py-24 px-6">
            <div className="max-w-4xl mx-auto flex flex-col items-center gap-8 text-center">
              <div className="relative w-full aspect-video rounded-2xl overflow-hidden shadow-2xl border border-primary/20">
                <img className="w-full h-full object-cover" alt="Modern clean software dashboard interface on a computer screen" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBUeZSXRlL5REYQw6zLueHk7ghJhazoiHQe_N2f2hLw1aSJzgUx87638viMAlwOU1ReFQ-W3AYbgvRD42UmAkwJmb86eSFEVDPsOaLo3EmF9SZB-A5Gp1_fZYceOtMnQDacl0IIie14e6pDb0Mfug0OrC0_CX07qMYym2pc4txymzxlqk0dpri1_hYBoaBwC3kqrrLY6oa6QVJINshoWmvbM4enA4lgLiVz9al_eH9FvzCqySIvtAXY0xrgB_iG4SH9ic7SNzpPF98" />
                <div className="absolute inset-0 bg-gradient-to-t from-primary/20 to-transparent"></div>
              </div>
              <div className="mt-8">
                <h2 className="text-3xl font-bold mb-4">Ready to improve your user experience?</h2>
                <p className="text-lg text-slate-600 mb-8">Join hundreds of developers making the web more inclusive for everyone.</p>
                <button className="bg-primary hover:bg-primary/90 text-white font-bold h-14 px-10 rounded-xl transition-all shadow-xl shadow-primary/25 cursor-pointer">
                  Get Started for Free
                </button>
              </div>
            </div>
          </section>
        </main>
        <footer className="px-6 py-12 border-t border-slate-200 text-center">
          <div className="flex flex-wrap justify-center gap-8 mb-8">
            <a className="text-slate-500 hover:text-primary transition-colors text-sm font-medium" href="#">Privacy Policy</a>
            <a className="text-slate-500 hover:text-primary transition-colors text-sm font-medium" href="#">Terms of Service</a>
            <a className="text-slate-500 hover:text-primary transition-colors text-sm font-medium" href="#">Accessibility Statement</a>
            <a className="text-slate-500 hover:text-primary transition-colors text-sm font-medium" href="#">Contact Us</a>
          </div>
          <div className="flex items-center justify-center gap-2 text-slate-400 text-sm">
            <span className="material-symbols-outlined text-lg">copyright</span>
            <span>2024 CogniEase. Empowering inclusive design.</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
