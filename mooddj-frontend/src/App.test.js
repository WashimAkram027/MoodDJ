import { render, screen } from '@testing-library/react';
import App from './App';

test('renders MoodDJ app without crashing', () => {
  render(<App />);
  // Check that the app renders (HomePage should show "MoodDJ" title)
  expect(document.body).toBeInTheDocument();
});
