import { useState } from 'react';
import './App.css';

function App() {
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const serverUrl = `http://${window.location.hostname}:5000`;

  const skipToNext = async () => {
    try {
      await fetch(`${serverUrl}/next-photo`, { method: 'PUT' });
      setError(null);
    } catch (err) {
      setError('Failed to skip photo');
    }
  };

  const toggleBlackScreen = async () => {
    try {
      await fetch(`${serverUrl}/black-screen`, { method: 'PUT' });
      setError(null);
    } catch (err) {
      setError('Failed to toggle black screen');
    }
  };

  const openInGooglePhotos = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${serverUrl}/current-photo-url`);
      const data = await response.json();
      if (response.ok) {
        // Open window first before async operation
        const newWindow = window.open('about:blank', '_blank');
        if (newWindow) {
          newWindow.location.href = data.url;
        } else {
          setError('Popup was blocked. Please allow popups for this site.');
        }
        setError(null);
      } else {
        setError(data.error || 'Failed to get photo URL');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Slideshow Control</h1>
        <div className="button-container">
          <button onClick={skipToNext}>
            Next Photo
          </button>
          <button onClick={toggleBlackScreen}>
            Toggle Black Screen
          </button>
          <button 
            onClick={openInGooglePhotos}
            disabled={isLoading}
          >
            {isLoading ? 'Loading...' : 'Open current photo in Google Photos'}
          </button>
        </div>
        {error && <p className="error">{error}</p>}
        <p className="server-info">Connected to: {serverUrl}</p>
      </header>
    </div>
  );
}

export default App; 