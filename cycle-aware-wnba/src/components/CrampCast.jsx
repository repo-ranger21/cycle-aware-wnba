import React, { useState } from "react";

export default function CrampCast({ showAlerts }) {
  const [alertsEnabled, setAlertsEnabled] = useState(showAlerts);

  return (
    <div className="bg-red-100 rounded-lg shadow-md p-6 mb-6 relative">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xl font-bold text-red-700">🩸 CrampCast™</h2>
        <span className="text-xs bg-red-300 text-white px-2 py-1 rounded">Live from the Luteal Zone</span>
      </div>
      <p className="mb-2 font-medium text-red-500">Forecast: <span className="font-bold">70% chance of irrational rage</span></p>
      <div className="mb-2 text-sm">
        <span className="font-bold">Cycle Phase:</span> Luteal (Day 24)
      </div>
      <div className="mb-2 text-sm">
        <span className="font-bold">Predicted Symptoms:</span> Cramps, Mood Swings, Bloating
      </div>
      <div className="mb-2 text-sm">
        <span className="font-bold">Performance Impact:</span> -3.2% agility, +12% clutch irrationality
      </div>
      <div className="mb-2 text-sm italic border-l-4 border-pink-400 pl-2">
        Coach Tip: “Bench the ego, not the athlete.”
      </div>
      <button
        className={`px-4 py-2 mt-4 rounded bg-pink-600 text-white font-semibold hover:bg-pink-700 transition`}
        onClick={() => setAlertsEnabled((prev) => !prev)}
      >
        {alertsEnabled ? "Disable Alerts" : "Enable Alerts"}
      </button>
      <div className="absolute top-2 right-2 group">
        <span className="text-xs text-gray-400 underline cursor-pointer">?</span>
        <div className="hidden group-hover:block absolute z-10 bg-white border border-gray-300 rounded p-2 w-64 shadow-lg text-gray-600 text-xs">
          CrampCast™ is satire. It mocks the idea that athletes can be reduced to hormone charts. Use it to reflect, not to stereotype.
        </div>
      </div>
    </div>
  );
}