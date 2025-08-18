import React, { useState, useEffect } from 'react';

// TypeScript interfaces for data structures
interface VolatilityFlags {
  volatility_index: number; // 0 to 1
  cycle_phase_tag: string; // e.g., "Synthetic Luteal"
  fatigue_score: number; // 0 to 100
}

interface SportsProjection {
  id: string;
  league: string;
  matchup: string;
  projected_winner: string;
  confidence_score: number;
  source: string;
  volatility_flags: VolatilityFlags;
}

// Mock API data
const mockProjectionsData: SportsProjection[] = [
  {
    id: '1',
    league: 'WNBA',
    matchup: 'Las Vegas Aces vs Chicago Sky',
    projected_winner: 'Las Vegas Aces',
    confidence_score: 0.72,
    source: 'Covers',
    volatility_flags: {
      volatility_index: 0.3,
      cycle_phase_tag: 'Synthetic Luteal',
      fatigue_score: 24
    }
  },
  {
    id: '2',
    league: 'WNBA',
    matchup: 'Seattle Storm vs New York Liberty',
    projected_winner: 'New York Liberty',
    confidence_score: 0.65,
    source: 'OddsCrowd',
    volatility_flags: {
      volatility_index: 0.45,
      cycle_phase_tag: 'Follicular Phase',
      fatigue_score: 18
    }
  },
  {
    id: '3',
    league: 'NFL',
    matchup: 'Kansas City Chiefs vs Buffalo Bills',
    projected_winner: 'Kansas City Chiefs',
    confidence_score: 0.58,
    source: 'OddsTrader',
    volatility_flags: {
      volatility_index: 0.62,
      cycle_phase_tag: 'Ovulation Peak',
      fatigue_score: 41
    }
  },
  {
    id: '4',
    league: 'MLB',
    matchup: 'Los Angeles Dodgers vs Atlanta Braves',
    projected_winner: 'Los Angeles Dodgers',
    confidence_score: 0.68,
    source: 'Covers',
    volatility_flags: {
      volatility_index: 0.28,
      cycle_phase_tag: 'Menstrual Recovery',
      fatigue_score: 15
    }
  },
  {
    id: '5',
    league: 'WNBA',
    matchup: 'Phoenix Mercury vs Connecticut Sun',
    projected_winner: 'Connecticut Sun',
    confidence_score: 0.74,
    source: 'OddsCrowd',
    volatility_flags: {
      volatility_index: 0.51,
      cycle_phase_tag: 'Pre-Ovulation',
      fatigue_score: 32
    }
  },
  {
    id: '6',
    league: 'NFL',
    matchup: 'Green Bay Packers vs Detroit Lions',
    projected_winner: 'Green Bay Packers',
    confidence_score: 0.61,
    source: 'OddsTrader',
    volatility_flags: {
      volatility_index: 0.39,
      cycle_phase_tag: 'Luteal Stability',
      fatigue_score: 27
    }
  }
];

type SortField = 'league' | 'matchup' | 'projected_winner' | 'confidence_score' | 'source';
type SortDirection = 'asc' | 'desc';

const LiveProjectionsPanel: React.FC = () => {
  const [projections, setProjections] = useState<SportsProjection[]>([]);
  const [loading, setLoading] = useState(true);
  const [showVolatilityFlags, setShowVolatilityFlags] = useState(true);
  const [ethicsMode, setEthicsMode] = useState(false);
  const [satiricalOverlays, setSatiricalOverlays] = useState(true);
  const [sortField, setSortField] = useState<SortField>('confidence_score');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  // Mock API fetch
  useEffect(() => {
    const fetchProjections = async () => {
      setLoading(true);
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      setProjections(mockProjectionsData);
      setLoading(false);
    };

    fetchProjections();
  }, []);

  // Sort projections
  const sortedProjections = [...projections].sort((a, b) => {
    let aValue, bValue;
    
    switch (sortField) {
      case 'confidence_score':
        aValue = a.confidence_score;
        bValue = b.confidence_score;
        break;
      default:
        aValue = a[sortField];
        bValue = b[sortField];
    }

    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  // Handle sort
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Mock Supabase function
  const pushToSupabase = async () => {
    alert('Mock: Picks pushed to Supabase successfully! 🎯');
    console.log('Pushing projections to Supabase:', projections);
  };

  // Get volatility color
  const getVolatilityColor = (index: number) => {
    if (index < 0.3) return 'text-green-600';
    if (index < 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Get fatigue color
  const getFatigueColor = (score: number) => {
    if (score < 30) return 'text-green-600';
    if (score < 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-xl p-8">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            <div className="h-4 bg-gray-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 lg:mb-0">
          Live Volatility Projections Panel
        </h2>
        <button
          onClick={pushToSupabase}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
        >
          Push picks to Supabase
        </button>
      </div>

      {/* Contributor Toggles */}
      <div className="mb-6 space-y-4">
        <div className="flex flex-wrap gap-4 items-center">
          <button
            onClick={() => setShowVolatilityFlags(!showVolatilityFlags)}
            className={`px-4 py-2 rounded font-semibold transition ${
              showVolatilityFlags
                ? 'bg-purple-600 text-white hover:bg-purple-700'
                : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
            }`}
          >
            {showVolatilityFlags ? 'Hide Volatility Flags' : 'Show Volatility Flags'}
          </button>
          
          <button
            onClick={() => setEthicsMode(!ethicsMode)}
            className={`px-4 py-2 rounded font-semibold transition ${
              ethicsMode
                ? 'bg-green-700 text-white hover:bg-green-800'
                : 'bg-pink-600 text-white hover:bg-pink-700'
            }`}
          >
            {ethicsMode ? 'Switch to Satire Mode' : 'Switch to Ethics Mode'}
          </button>

          <button
            onClick={() => setSatiricalOverlays(!satiricalOverlays)}
            className={`px-4 py-2 rounded font-semibold transition ${
              satiricalOverlays
                ? 'bg-orange-600 text-white hover:bg-orange-700'
                : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
            }`}
          >
            {satiricalOverlays ? 'Hide Satirical Overlays' : 'Show Satirical Overlays'}
          </button>
        </div>

        <div className="text-xs text-gray-500">
          {ethicsMode
            ? 'Ethics Mode: Civic-grade volatility modeling with dignity and transparency.'
            : 'Satire Mode: Playful volatility overlays enabled for experimental purposes.'}
        </div>
      </div>

      {/* Projections Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-50">
              <th 
                className="border border-gray-300 px-4 py-3 text-left font-semibold cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('league')}
              >
                League {sortField === 'league' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th 
                className="border border-gray-300 px-4 py-3 text-left font-semibold cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('matchup')}
              >
                Matchup {sortField === 'matchup' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th 
                className="border border-gray-300 px-4 py-3 text-left font-semibold cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('projected_winner')}
              >
                Projected Winner {sortField === 'projected_winner' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th 
                className="border border-gray-300 px-4 py-3 text-left font-semibold cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('confidence_score')}
              >
                Confidence Score {sortField === 'confidence_score' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th 
                className="border border-gray-300 px-4 py-3 text-left font-semibold cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('source')}
              >
                Source {sortField === 'source' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              {showVolatilityFlags && (
                <th className="border border-gray-300 px-4 py-3 text-left font-semibold">
                  Volatility Metrics
                </th>
              )}
            </tr>
          </thead>
          <tbody>
            {sortedProjections.map((projection) => (
              <tr key={projection.id} className="hover:bg-gray-50">
                <td className="border border-gray-300 px-4 py-3">
                  <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                    projection.league === 'WNBA' ? 'bg-pink-100 text-pink-800' :
                    projection.league === 'NFL' ? 'bg-blue-100 text-blue-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {projection.league}
                  </span>
                </td>
                <td className="border border-gray-300 px-4 py-3 font-medium">
                  {projection.matchup}
                </td>
                <td className="border border-gray-300 px-4 py-3 font-semibold text-blue-600">
                  {projection.projected_winner}
                </td>
                <td className="border border-gray-300 px-4 py-3">
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${projection.confidence_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">
                      {(projection.confidence_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </td>
                <td className="border border-gray-300 px-4 py-3">
                  <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                    projection.source === 'Covers' ? 'bg-purple-100 text-purple-800' :
                    projection.source === 'OddsCrowd' ? 'bg-orange-100 text-orange-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {projection.source}
                  </span>
                </td>
                {showVolatilityFlags && (
                  <td className="border border-gray-300 px-4 py-3">
                    <div className="space-y-1 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-600">Volatility:</span>
                        <span className={`font-semibold ${getVolatilityColor(projection.volatility_flags.volatility_index)}`}>
                          {(projection.volatility_flags.volatility_index * 100).toFixed(1)}%
                        </span>
                      </div>
                      {satiricalOverlays && (
                        <>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">Phase:</span>
                            <span className="font-medium text-pink-600">
                              {projection.volatility_flags.cycle_phase_tag}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">Fatigue:</span>
                            <span className={`font-semibold ${getFatigueColor(projection.volatility_flags.fatigue_score)}`}>
                              {projection.volatility_flags.fatigue_score}/100
                            </span>
                          </div>
                        </>
                      )}
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Civic Disclaimer */}
      <div className="mt-8 p-4 bg-gray-50 border border-gray-300 rounded-lg">
        <p className="text-sm text-gray-700 leading-relaxed">
          <strong>Civic Disclaimer:</strong> These projections are for civic experimentation only. 
          No biometric data used. No cramps exploited. Volatility flags are synthetic and satirical. 
          All modeling prioritizes athlete dignity and contributor clarity through civic-grade ethics.
        </p>
      </div>
    </div>
  );
};

export default LiveProjectionsPanel;