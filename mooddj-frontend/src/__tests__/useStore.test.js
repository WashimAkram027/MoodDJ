/**
 * ZUSTAND STORE TEST SUITE
 * 
 * Module: useStore (Global State Management)
 * Purpose: Tests centralized application state
 * 
 * What this module does in the app:
 * - Stores current mood across all components
 * - Stores current playing track globally
 * - Maintains mood history (last 10 detections)
 * - Shares state between VideoFeed, MusicPlayer, Dashboard
 * 
 * Why we test it:
 * - State is the "single source of truth"
 * - Bugs here affect entire app
 * - Memory leaks from unlimited history
 */

import { renderHook, act } from '@testing-library/react';
import useStore from '../store/useStore';

describe('Zustand Store', () => {
  /**
   * Test Case 1: Set Current Mood
   * 
   * Purpose: Verify mood updates propagate globally
   * Input: Set mood to 'happy' with 0.9 confidence
   * Expected Output: All components see new mood
   * Tests: Global state update mechanism
   * 
   * Why this matters:
   * - VideoFeed detects mood → MusicPlayer updates playlist
   * - Dashboard displays current mood
   * - History tracks mood over time
   * 
   * Real-world scenario:
   * Camera detects happiness → Entire UI updates to show happy state
   */
  test('setCurrentMood updates mood state', () => {
    const { result } = renderHook(() => useStore());

    act(() => {
      result.current.setCurrentMood('happy', 0.9);
    });

    expect(result.current.currentMood).toBe('happy');
    expect(result.current.moodConfidence).toBe(0.9);
    expect(result.current.moodHistory).toHaveLength(1);
  });

  /**
   * Test Case 2: Set Current Track
   * 
   * Purpose: Verify track updates propagate globally
   * Input: Set track object with id, title, artist
   * Expected Output: All components see new track
   * Tests: Track state management
   * 
   * Why this matters:
   * - MusicPlayer plays track → Dashboard shows "Now Playing"
   * - Multiple components display same track info
   * - Prevents desync between UI elements
   * 
   * Real-world scenario:
   * Song starts playing → UI updates to show track details everywhere
   */
  test('setCurrentTrack updates track state', () => {
    const { result } = renderHook(() => useStore());
    const mockTrack = {
      id: 'track123',
      title: 'Test Song',
      artist: 'Test Artist'
    };

    act(() => {
      result.current.setCurrentTrack(mockTrack);
    });

    expect(result.current.currentTrack).toEqual(mockTrack);
  });

  /**
   * Test Case 3: Mood History Size Limit
   * 
   * Purpose: Verify history doesn't grow infinitely
   * Input: Add 15 moods to history
   * Expected Output: Only last 10 moods stored
   * Tests: Memory management
   * 
   * Why this matters:
   * - Prevents memory leaks from storing 1000s of moods
   * - App runs for hours detecting mood every 3 seconds
   * - Without limit, would store 1200 moods/hour
   * 
   * Real-world scenario:
   * User runs app all day → Memory stays constant, doesn't grow
   */
  test('moodHistory maintains size limit', () => {
    const { result } = renderHook(() => useStore());

    act(() => {
      for (let i = 0; i < 15; i++) {
        result.current.setCurrentMood('happy', 0.8);
      }
    });

    expect(result.current.moodHistory).toHaveLength(10);
  });
});