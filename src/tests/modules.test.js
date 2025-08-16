/**
 * Test suite for Q4Trackr modules
 */

const MoodMeeter = require('../modules/MoodMeeter');
const CrampCast = require('../modules/CrampCast');
const MoodSwingMeter = require('../modules/MoodSwingMeter');
const Ovulytics = require('../modules/Ovulytics');

describe('Q4Trackr Satirical Modules', () => {
  const testPlayer = 'Test Player';
  const testDate = '2024-03-15';

  describe('MoodMeeter™', () => {
    let moodMeeter;

    beforeEach(() => {
      moodMeeter = new MoodMeeter();
    });

    test('should analyze mood with proper structure', async () => {
      const result = await moodMeeter.analyzeMood(testPlayer, testDate);
      
      expect(result).toHaveProperty('player', testPlayer);
      expect(result).toHaveProperty('module', 'MoodMeeter™');
      expect(result).toHaveProperty('moodIndex');
      expect(result).toHaveProperty('emoji');
      expect(result).toHaveProperty('ethicalNotice');
      expect(result.moodIndex).toBeGreaterThanOrEqual(1);
      expect(result.moodIndex).toBeLessThanOrEqual(10);
    });

    test('should include satirical elements', async () => {
      const result = await moodMeeter.analyzeMood(testPlayer, testDate);
      
      expect(result).toHaveProperty('tooltip');
      expect(result).toHaveProperty('factors');
      expect(['😡', '😃', '😭', '😐', '🧘']).toContain(result.emoji);
    });
  });

  describe('CrampCast™', () => {
    let crampCast;

    beforeEach(() => {
      crampCast = new CrampCast();
    });

    test('should predict cramps with proper structure', async () => {
      const result = await crampCast.predictCramps(testPlayer, testDate);
      
      expect(result).toHaveProperty('player', testPlayer);
      expect(result).toHaveProperty('module', 'CrampCast™');
      expect(result).toHaveProperty('probability');
      expect(result).toHaveProperty('severity');
      expect(result).toHaveProperty('ethicalNotice');
      expect(result.probability).toBeGreaterThanOrEqual(0);
      expect(result.probability).toBeLessThanOrEqual(100);
      expect(result.severity).toBeGreaterThanOrEqual(1);
      expect(result.severity).toBeLessThanOrEqual(5);
    });

    test('should include satirical severity info', async () => {
      const result = await crampCast.predictCramps(testPlayer, testDate);
      
      expect(result).toHaveProperty('severityInfo');
      expect(result.severityInfo).toHaveProperty('emoji');
      expect(result.severityInfo).toHaveProperty('tooltip');
    });
  });

  describe('MoodSwingMeter™', () => {
    let moodSwingMeter;

    beforeEach(() => {
      moodSwingMeter = new MoodSwingMeter();
    });

    test('should analyze mood swings with proper structure', async () => {
      const result = await moodSwingMeter.analyzeMoodSwings(testPlayer, testDate);
      
      expect(result).toHaveProperty('player', testPlayer);
      expect(result).toHaveProperty('module', 'MoodSwingMeter™');
      expect(result).toHaveProperty('level');
      expect(result).toHaveProperty('emoji');
      expect(result).toHaveProperty('volatilityScore');
      expect(['Stable', 'Moderate', 'Turbulent']).toContain(result.level);
      expect(['🌈', '🌊', '🌪️']).toContain(result.emoji);
    });

    test('should include factor analysis', async () => {
      const result = await moodSwingMeter.analyzeMoodSwings(testPlayer, testDate);
      
      expect(result).toHaveProperty('factors');
      expect(result.factors).toHaveProperty('sleep');
      expect(result.factors).toHaveProperty('social');
      expect(result.factors).toHaveProperty('schedule');
    });
  });

  describe('Ovulytics™', () => {
    let ovulytics;

    beforeEach(() => {
      ovulytics = new Ovulytics();
    });

    test('should track ovulation with proper structure', async () => {
      const result = await ovulytics.trackOvulation(testPlayer, testDate);
      
      expect(result).toHaveProperty('player', testPlayer);
      expect(result).toHaveProperty('module', 'Ovulytics™');
      expect(result).toHaveProperty('phase');
      expect(result).toHaveProperty('emoji');
      expect(result).toHaveProperty('cycleDay');
      expect(['Follicular', 'Ovulation', 'Luteal']).toContain(result.phase);
      expect(['🌑', '🌕', '🌘']).toContain(result.emoji);
    });

    test('should include performance factors', async () => {
      const result = await ovulytics.trackOvulation(testPlayer, testDate);
      
      expect(result).toHaveProperty('performanceFactors');
      expect(result.performanceFactors).toHaveProperty('energy');
      expect(result.performanceFactors).toHaveProperty('focus');
      expect(result).toHaveProperty('performancePrediction');
    });
  });

  describe('Integration Tests', () => {
    test('all modules should maintain ethical standards', async () => {
      const modules = [
        new MoodMeeter(),
        new CrampCast(),
        new MoodSwingMeter(),
        new Ovulytics()
      ];

      for (const module of modules) {
        const info = module.getModuleInfo();
        expect(info).toHaveProperty('ethicalNotice');
        expect(info.ethicalNotice.toLowerCase()).toContain('satirical');
      }
    });

    test('all modules should support sample JSON output format', async () => {
      const moodMeeter = new MoodMeeter();
      const crampCast = new CrampCast();
      const moodSwingMeter = new MoodSwingMeter();
      const ovulytics = new Ovulytics();

      const moodResult = await moodMeeter.analyzeMood(testPlayer, testDate);
      const crampResult = await crampCast.predictCramps(testPlayer, testDate);
      const swingResult = await moodSwingMeter.analyzeMoodSwings(testPlayer, testDate);
      const ovulationResult = await ovulytics.trackOvulation(testPlayer, testDate);

      // Should be able to construct the expected JSON format
      const combinedResult = {
        player: testPlayer,
        mood_index: moodResult.moodIndex,
        cramp_severity: crampResult.severity,
        mood_swing: swingResult.level,
        ovulation_phase: ovulationResult.phase
      };

      expect(combinedResult).toHaveProperty('player');
      expect(combinedResult).toHaveProperty('mood_index');
      expect(combinedResult).toHaveProperty('cramp_severity');
      expect(combinedResult).toHaveProperty('mood_swing');
      expect(combinedResult).toHaveProperty('ovulation_phase');
    });
  });
});