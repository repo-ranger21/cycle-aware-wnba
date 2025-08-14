import React from "react";

export default function Ovulytics({ day }) {
  const isOvulation = day === 14;
  return (
    <div className="bg-yellow-100 rounded-lg shadow-md p-6 mb-6 relative">
      <h2 className="text-lg font-bold text-yellow-700">🥚 Ovulytics™</h2>
      <div className="mt-2 text-sm">
        {isOvulation ? (
          <span>
            Ovulation detected. <span className="font-bold">Proceed with caution and extra hydration.</span>
          </span>
        ) : (
          <span>
            Day {day} of cycle. No ovulation detected.
          </span>
        )}
      </div>
      <div className="text-xs text-gray-400 italic mt-2">
        Ovulytics™ is satire. Ovulation is not a performance predictor.
      </div>
    </div>
  );
}