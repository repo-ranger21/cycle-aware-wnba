import React from "react";

export default function EthicsToggle({ ethicsMode, setEthicsMode }) {
  return (
    <div className="mb-6 flex items-center gap-3">
      <button
        className={`px-4 py-2 rounded font-semibold transition ${
          ethicsMode
            ? "bg-green-700 text-white hover:bg-green-800"
            : "bg-pink-600 text-white hover:bg-pink-700"
        }`}
        onClick={() => setEthicsMode((prev) => !prev)}
      >
        {ethicsMode ? "Switch to Satire Mode" : "Switch to Ethics Mode"}
      </button>
      <span className="text-xs text-gray-500">
        {ethicsMode
          ? "Ethics Mode: Civic-grade cycle insights with dignity and transparency."
          : "Satire Mode: Playful overlays enabled."}
      </span>
    </div>
  );
}