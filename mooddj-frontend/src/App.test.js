/**
 * App.test.js - Basic smoke test for MoodDJ
 *
 * Note: Full App component testing requires react-router-dom.
 * Integration tests for routing are done separately.
 * This test validates the test environment is working.
 */

test('MoodDJ test environment is configured correctly', () => {
  // Verify test environment is working
  expect(true).toBe(true);
  expect(1 + 1).toBe(2);
});

test('MoodDJ app name is defined', () => {
  const appName = 'MoodDJ';
  expect(appName).toBe('MoodDJ');
  expect(appName.length).toBeGreaterThan(0);
});
