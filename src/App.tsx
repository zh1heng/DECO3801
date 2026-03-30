import React, { useState } from 'react';
import LandingPage from './components/LandingPage';
import AnalyzingPage from './components/AnalyzingPage';
import DashboardPage from './components/DashboardPage';

export default function App() {
  const [currentView, setCurrentView] = useState<'landing' | 'analyzing' | 'dashboard'>('landing');

  const handleCheckWebsite = () => {
    setCurrentView('analyzing');
    setTimeout(() => {
      setCurrentView('dashboard');
    }, 15000);
  };

  const handleRescan = () => {
    setCurrentView('landing');
  };

  return (
    <div className="min-h-screen bg-background-light text-slate-900 font-display">
      {currentView === 'landing' && <LandingPage onCheck={handleCheckWebsite} />}
      {currentView === 'analyzing' && <AnalyzingPage />}
      {currentView === 'dashboard' && <DashboardPage onRescan={handleRescan} />}
    </div>
  );
}
