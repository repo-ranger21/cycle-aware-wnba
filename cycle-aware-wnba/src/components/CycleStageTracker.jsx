import React from "react";

// Cycle stages with humorous commentary
const stages = [
  { name: "Menstruation", start: 1, end: 5, joke: "Bleeding hearts club: now recruiting." },
  { name: "Follicular", start: 6, end: 13, joke: "Egg prepping: brunch vibes only." },
  { name: "Ovulation", start: 14, end: 16, joke: "Egg drop soup: spicy edition." },
  { name: "Luteal", start: 17, end: 28, joke: "Cramp Olympics: gold medal guaranteed." },
];

function getStage(day) {
  for (const stage of stages) {
    if (day >= stage.start && day <= stage.end) {
      return stage;
    }
  }
  return { name: "Unknown", joke: "Cycle mysteries abound..." };
}

export default function CycleStageTracker({ day }) {
  const { name, joke } = getStage(day);

  return (
    <div className="bg-white shadow-md rounded-lg p-6 flex flex-col items-center">
      <h2 className="text-xl font-semibold text-red-600 mb-2">
        CycleStageTracker™
      </h2>
      <div className="w-32 h-32 flex items-center justify-center rounded-full bg-gradient-to-tr from-red-200 to-pink-100 mb-3 border-4 border-red-400">
        <span className="text-lg font-bold text-red-500">{name}</span>
      </div>
      <p className="text-center text-pink-700 font-medium">
        {joke}
      </p>
      <span className="text-xs text-gray-400 mt-2">Day {day} of 28</span>
    </div>
  );
}