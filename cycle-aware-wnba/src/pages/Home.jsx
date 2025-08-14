import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white">
      <h1 className="text-4xl font-bold mb-6 text-gray-800">Welcome to Q4Trackr</h1>
      <p className="mb-8 text-center text-gray-500">
        Ethical, cycle-aware WNBA prediction platform. Transparency, dignity, and a splash of satire.
      </p>
      <Link
        to="/dashboard"
        className="inline-block px-6 py-3 mb-4 bg-green-600 text-white font-bold rounded-lg shadow-lg hover:bg-green-700 transition-all text-lg"
      >
        🧠 Go to Dashboard
      </Link>
      <Link
        to="/crampcast"
        className="inline-block px-6 py-3 bg-pink-600 text-white font-bold rounded-lg shadow-lg hover:bg-pink-700 transition-all text-lg"
      >
        🎙️ Visit CrampCast™
      </Link>
    </div>
  );
}