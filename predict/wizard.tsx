import React from 'react';
import LiveProjectionsPanel from '../src/components/LiveProjectionsPanel';

const PredictionWizard: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 to-yellow-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-pink-700 mb-8">Q4Trackr Prediction Wizard</h1>
        <LiveProjectionsPanel />
      </div>
    </div>
  );
};

export default PredictionWizard;