import React, { useState } from 'react';
import LandingPage from './components/LandingPage';
import AnalyzingPage from './components/AnalyzingPage';
import DashboardPage from './components/DashboardPage';

export interface AnalyzeResult {
  vh_score: number;
  nav_score: number;
  lang_score: number;
  total_score: number;
  reasons: string[];
}

export default function App() {
  const [currentView, setCurrentView] = useState<'landing' | 'analyzing' | 'dashboard'>('landing');
  const [analyzedUrl, setAnalyzedUrl] = useState('');
  const [analyzeResult, setAnalyzeResult] = useState<AnalyzeResult | null>(null);

  const handleCheckWebsite = async (url: string) => {
    setAnalyzedUrl(url);
    setCurrentView('analyzing');
    
    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze website');
      }
      
      const data: AnalyzeResult = await response.json();
      setAnalyzeResult(data);
    } catch (error) {
      console.error(error);
      alert('Error analyzing website. Please check the backend is running.');
    } finally {
      setCurrentView('dashboard');
    }
  };

  const handleRescan = () => {
    setCurrentView('landing');
    setAnalyzeResult(null);
    setAnalyzedUrl('');
  };

  return (
    <div className="min-h-screen bg-background-light text-slate-900 font-display">
      {currentView === 'landing' && <LandingPage onCheck={handleCheckWebsite} />}
      {currentView === 'analyzing' && <AnalyzingPage />}
      {currentView === 'dashboard' && <DashboardPage onRescan={handleRescan} analyzedUrl={analyzedUrl} result={analyzeResult} />}
    </div>
  );
}
