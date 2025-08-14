import React, { useState } from "react";
import CrampCast from "../components/CrampCast";
import Ovulytics from "../components/Ovulytics";
import EthicsToggle from "../components/EthicsToggle";

export default function Dashboard() {
  const [ethicsMode, setEthicsMode] = useState(false);

  // Mock data
  const day = 24;
  const showAlerts = true;

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 to-yellow-50 p-8">
      <div className="max-w-3xl mx-auto">
        <EthicsToggle ethicsMode={ethicsMode} setEthicsMode={setEthicsMode} />
        <div className="bg-white rounded-lg shadow-xl p-8">
          {!ethicsMode ? (
            <>
              <h1 className="text-2xl font-bold text-pink-700 mb-4">Q4Trackr Satirical Dashboard</h1>
              <CrampCast showAlerts={showAlerts} />
              <Ovulytics day={day} />
            </>
          ) : (
            <>
              <h1 className="text-2xl font-bold text-green-800 mb-4">Cycle Transparency Dashboard</h1>
              <p className="mb-6 text-gray-700">
                This dashboard provides civic-grade cycle insights with dignity and transparency.
              </p>
              {/* Replace overlays with anonymized, respectful data summaries */}
              <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-4 rounded">
                <p className="font-semibold text-green-700">Cycle Phase Summary</p>
                <ul className="mt-2 text-sm text-green-900">
                  <li>Current Phase: Luteal</li>
                  <li>Day in Cycle: 24</li>
                  <li>Average Reported Symptoms: Moderate</li>
                  <li>Performance Impact: Within normal range</li>
                  <li>Coach Tip: Support self-advocacy and adjust training as needed.</li>
                </ul>
              </div>
              <div className="bg-white border border-gray-300 rounded p-4 text-xs text-gray-600">
                All data is anonymized and opt-in. No individual athlete is identified. Outputs are for civic transparency only.
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}