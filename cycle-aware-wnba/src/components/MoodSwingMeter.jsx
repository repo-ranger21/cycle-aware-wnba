import React from "react";

// Satirical mood labels
const moodLabels = [
  "Zen Goddess",
  "Mildly Miffed",
  "Moody Megatron",
  "Storm Incoming",
  "Full Drama Llama",
];

export default function MoodSwingMeter({ moodLevel }) {
  // Clamp moodLevel between 1-5
  const level = Math.max(1, Math.min(moodLevel, 5));
  const moodLabel = moodLabels[level - 1];

  return (
    <div className="bg-white shadow-md rounded-lg p-6 flex flex-col items-center">
      <h2 className="text-xl font-semibold text-pink-700 mb-2">
        MoodSwingMeter™
      </h2>
      <div className="w-32 h-32 flex items-center justify-center rounded-full bg-gradient-to-tr from-pink-200 to-red-100 mb-3 border-4 border-pink-400">
        <span className="text-2xl font-bold text-red-500">{level}</span>
      </div>
      <p className="text-center font-medium text-pink-600">
        {moodLabel}
      </p>
      <span className="text-xs text-gray-400 mt-2">Scale: 1 (Zen) to 5 (Drama)</span>
    </div>
  );
}