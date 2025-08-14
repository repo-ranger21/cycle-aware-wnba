import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import CrampCast from "./pages/CrampCast";

export default function App() {
  return (
    <Router>
      <nav className="bg-pink-600 text-white py-3 flex justify-between px-8 shadow-lg">
        <div className="font-bold text-xl tracking-tight">Q4Trackr</div>
        <div className="flex gap-6">
          <Link to="/" className="hover:underline">Home</Link>
          <Link to="/dashboard" className="hover:underline">Dashboard</Link>
          <Link to="/crampcast" className="hover:underline">CrampCast™</Link>
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/crampcast" element={<CrampCast />} />
      </Routes>
    </Router>
  );
}