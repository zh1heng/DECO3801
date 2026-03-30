import React from 'react';
import { AnalyzeResult } from '../App';

export default function DashboardPage({ 
  onRescan, 
  analyzedUrl, 
  result 
}: { 
  onRescan: () => void; 
  analyzedUrl: string; 
  result: AnalyzeResult | null;
}) {
  const totalScore = result?.total_score ?? 5;
  const vhScore = result?.vh_score ?? 5;
  const navScore = result?.nav_score ?? 5;
  const langScore = result?.lang_score ?? 5;
  const layoutScore = 5;
  const animationScore = 5;
  return (
    <div className="relative flex min-h-screen flex-col bg-background-light text-slate-900 font-display">
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-primary/10 bg-white/80 px-6 py-4 backdrop-blur-md lg:px-10">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-white">
            <span className="material-symbols-outlined">psychology</span>
          </div>
          <div>
            <h2 className="text-xl font-bold tracking-tight text-primary">CogniEase</h2>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-widest">Accessibility Hub</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors cursor-pointer">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors cursor-pointer">
            <span className="material-symbols-outlined">settings</span>
          </button>
          <div className="h-10 w-10 rounded-full border-2 border-primary/20 bg-primary/10 bg-cover bg-center" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuBJ6fPbBgqwWa_7hB3mtIBs_GJKfFWIBsUkvSmJiDdwGw1Ba9cpM_alm7toCZ8KnxRKpnKOxRE8XVp5D-ASq01tRsn39w2PDsHkyWir5s_Jx35BKyi_JQH2oXaonjvZJ5CIngOlFhf2zrgTEeT_SrWpw8cdLzynLfsaCoMjNjvyU4pCWYrHC2AJRY-jJM9WSVEwHqWENR1tlam4M8Gkcdg2yW9A8i1qXBO26kpYZhBixfYHEsAeneBoixNZqbPZn4iVUM8W699qqgg")' }}></div>
        </div>
      </header>
      <main className="flex-1 px-6 py-8 lg:px-10">
        <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <h1 className="text-3xl font-black tracking-tight lg:text-4xl">CogniEase Dashboard</h1>
            <div className="mt-1 flex items-center gap-2 text-slate-500">
              <span className="material-symbols-outlined text-sm">language</span>
              <p className="text-sm font-medium">Website analysed: <span className="text-primary underline decoration-primary/30 underline-offset-4">{analyzedUrl || 'example.com'}</span></p>
            </div>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-bold border border-primary/10 shadow-sm cursor-pointer hover:bg-slate-50 transition-colors">
              <span className="material-symbols-outlined text-[18px]">download</span>
              Export PDF
            </button>
            <button onClick={onRescan} className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white shadow-lg shadow-primary/20 cursor-pointer hover:bg-primary/90 transition-colors">
              <span className="material-symbols-outlined text-[18px]">refresh</span>
              Re-scan Site
            </button>
          </div>
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          <div className="col-span-1 rounded-xl border border-primary/10 bg-white p-6 shadow-sm lg:col-span-4">
            <h3 className="text-lg font-bold text-slate-700">Overall Score</h3>
            <div className="mt-8 flex flex-col items-center justify-center">
              <div className="relative flex h-40 w-40 items-center justify-center rounded-full border-8 border-yellow-400/20">
                <div className="absolute inset-0 rounded-full border-8 border-yellow-400 border-t-transparent" style={{ transform: 'rotate(45deg)' }}></div>
                <div className="text-center">
                  <span className="text-4xl font-black">{totalScore}<span className="text-xl text-slate-400">/100</span></span>
                </div>
              </div>
              <div className="mt-6 inline-flex items-center gap-2 rounded-full bg-yellow-100 px-4 py-1 text-sm font-bold text-yellow-700">
                <span className="material-symbols-outlined text-[18px]">warning</span>
                Status: Moderate
              </div>
              <p className="mt-4 text-center text-sm text-slate-500">Your site is accessible to most, but cognitive friction exists in key areas.</p>
            </div>
          </div>
          <div className="col-span-1 flex flex-col rounded-xl border border-primary/10 bg-white p-6 shadow-sm lg:col-span-8">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-700">Cognitive Load Radar</h3>
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Live Metrics</span>
            </div>
            <div className="mt-6 flex flex-1 items-center justify-center min-h-[250px] relative">
              <div className="absolute inset-0 flex items-center justify-center opacity-10">
                <div className="h-48 w-48 rounded-full border border-primary"></div>
                <div className="absolute h-32 w-32 rounded-full border border-primary"></div>
                <div className="absolute h-16 w-16 rounded-full border border-primary"></div>
              </div>
              <svg className="relative z-10 h-full w-full max-w-[400px]" preserveAspectRatio="xMidYMid meet" viewBox="0 0 100 100">
                {(() => {
                  const metrics = [vhScore, navScore, layoutScore, langScore, animationScore];
                  const maxRadius = 37.5;
                  const center = 50;
                  const points = metrics.map((score, i) => {
                    const angleRad = (-90 + (i * 72)) * Math.PI / 180;
                    const r = (score / 100) * maxRadius;
                    return {
                      x: center + r * Math.cos(angleRad),
                      y: center + r * Math.sin(angleRad)
                    };
                  });
                  const polygonPoints = points.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
                  
                  return (
                    <>
                      <polygon fill="rgba(43, 140, 238, 0.2)" points={polygonPoints} stroke="#2b8cee" strokeWidth="1"></polygon>
                      {points.map((p, i) => (
                        <circle key={i} cx={p.x} cy={p.y} fill="#2b8cee" r="1.5"></circle>
                      ))}
                    </>
                  );
                })()}
              </svg>
              <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                <span className="absolute top-2 text-[10px] font-bold text-slate-400 uppercase">Visual Hierarchy ({vhScore})</span>
                <span className="absolute top-1/4 right-0 text-[10px] font-bold text-slate-400 uppercase">Nav Depth ({navScore})</span>
                <span className="absolute bottom-1/4 right-4 text-[10px] font-bold text-slate-400 uppercase">Layout Density ({layoutScore})</span>
                <span className="absolute bottom-1/4 left-4 text-[10px] font-bold text-slate-400 uppercase">Language ({langScore})</span>
                <span className="absolute top-1/4 left-0 text-[10px] font-bold text-slate-400 uppercase">Animation ({animationScore})</span>
              </div>
            </div>
          </div>
          <div className="col-span-1 rounded-xl border border-primary/10 bg-white p-6 shadow-sm lg:col-span-4">
            <h3 className="mb-6 text-lg font-bold text-slate-700">Category breakdown</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-green-500"></div>
                  <span className="text-sm font-medium">Visual Hierarchy</span>
                </div>
                <span className="text-sm font-bold">{vhScore}</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-blue-500"></div>
                  <span className="text-sm font-medium">Navigation Depth</span>
                </div>
                <span className="text-sm font-bold">{navScore}</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-yellow-500"></div>
                  <span className="text-sm font-medium">Layout Density</span>
                </div>
                <span className="text-sm font-bold">{layoutScore}</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-orange-500"></div>
                  <span className="text-sm font-medium">Language Simplicity</span>
                </div>
                <span className="text-sm font-bold">{langScore}</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-red-500"></div>
                  <span className="text-sm font-medium">Animation Distraction</span>
                </div>
                <span className="text-sm font-bold text-red-500">{animationScore}</span>
              </div>
            </div>
          </div>
          <div className="col-span-1 rounded-xl border border-primary/10 bg-white p-6 shadow-sm lg:col-span-4">
            <h3 className="mb-6 text-lg font-bold text-slate-700">Key Friction Points</h3>
            <div className="space-y-4">
              <div className="flex gap-4 rounded-lg bg-red-50 p-3">
                <span className="material-symbols-outlined text-red-500">error</span>
                <div>
                  <p className="text-sm font-bold text-red-700">High Motion Detected</p>
                  <p className="text-xs text-red-600">Background animations cause significant cognitive distraction for ADHD users.</p>
                </div>
              </div>
              <div className="flex gap-4 rounded-lg bg-orange-50 p-3">
                <span className="material-symbols-outlined text-orange-500">report_problem</span>
                <div>
                  <p className="text-sm font-bold text-orange-700">Complex Terminology</p>
                  <p className="text-xs text-orange-600">Legal and technical jargon score above the recommended 8th-grade level.</p>
                </div>
              </div>
              <div className="flex gap-4 rounded-lg bg-yellow-50 p-3">
                <span className="material-symbols-outlined text-yellow-600">visibility_off</span>
                <div>
                  <p className="text-sm font-bold text-yellow-700">Low Contrast Ratio</p>
                  <p className="text-xs text-yellow-600">Tertiary text in the footer fails WCAG 2.1 contrast standards.</p>
                </div>
              </div>
            </div>
          </div>
          <div className="col-span-1 rounded-xl border border-primary/10 bg-white p-6 shadow-sm lg:col-span-4">
            <h3 className="mb-6 text-lg font-bold text-slate-700">Smart Suggestions</h3>
            <ul className="space-y-4">
              {result?.reasons?.length ? result.reasons.map((reason, i) => (
                <li key={i} className="flex items-start gap-3">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/20 text-primary">
                    <span className="material-symbols-outlined text-sm font-bold">priority_high</span>
                  </div>
                  <p className="text-sm text-slate-600">{reason}</p>
                </li>
              )) : (
                <li className="flex items-start gap-3">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/20 text-primary">
                    <span className="material-symbols-outlined text-sm font-bold">check</span>
                  </div>
                  <p className="text-sm text-slate-600">No major issues detected by current rules.</p>
                </li>
              )}
            </ul>
            <button className="mt-8 w-full rounded-lg bg-primary/10 py-3 text-sm font-bold text-primary hover:bg-primary transition-colors hover:text-white cursor-pointer">
              View Detailed Report
            </button>
          </div>
        </div>
      </main>
      <footer className="mt-12 border-t border-primary/10 bg-white px-6 py-6 lg:px-10">
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          <p className="text-xs font-medium text-slate-400">© 2024 CogniEase AI. All accessibility rights reserved.</p>
          <div className="flex gap-6">
            <a className="text-xs font-medium text-slate-400 hover:text-primary" href="#">Privacy Policy</a>
            <a className="text-xs font-medium text-slate-400 hover:text-primary" href="#">Terms of Service</a>
            <a className="text-xs font-medium text-slate-400 hover:text-primary" href="#">Documentation</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
