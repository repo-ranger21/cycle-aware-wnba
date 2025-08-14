import React from "react";
import MoodSwingMeter from "../components/MoodSwingMeter";
import CycleStageTracker from "../components/CycleStageTracker";

export default function CrampCast() {
  // Mock data
  const moodLevel = 3;
  const day = 17;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-pink-100">
      <h1 className="text-3xl font-bold text-red-700 mb-2">
        🩸 CrampCast™: Live from the Luteal Zone
      </h1>
      <p className="mb-8 text-center italic text-red-500">
        Broadcasting live from your uterus. No filter, no apologies.
      </p>
      <div className="w-full max-w-md space-y-10">
        <MoodSwingMeter moodLevel={moodLevel} />
        <CycleStageTracker day={day} />
      </div>
    </div>
  );
}