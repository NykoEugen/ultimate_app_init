import { useEffect, useState } from 'react';
import { usePlayerStore } from '../store/usePlayerStore.js';

const MIN_PLAYER_ID = 1;

function toSafeNumber(value) {
  const parsed = Number.parseInt(value, 10);
  return Number.isNaN(parsed) ? null : parsed;
}

const defaultHint = `Enter a player id ≥ ${MIN_PLAYER_ID}`;

function PlayerSwitcher() {
  const playerId = usePlayerStore((state) => state.playerId);
  const setPlayerId = usePlayerStore((state) => state.setPlayerId);
  const fetchDashboard = usePlayerStore((state) => state.fetchDashboard);
  const loading = usePlayerStore((state) => state.loadingDashboard);

  const [inputValue, setInputValue] = useState(playerId ?? '');
  const [message, setMessage] = useState(defaultHint);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    setInputValue(playerId ?? '');
  }, [playerId]);

  const validate = (value) => {
    const numeric = toSafeNumber(value);
    if (numeric === null) {
      setMessage('Player id must be a number.');
      setIsError(true);
      return { valid: false };
    }

    if (numeric < MIN_PLAYER_ID) {
      setMessage(`Minimum player id is ${MIN_PLAYER_ID}.`);
      setIsError(true);
      return { valid: false };
    }

    setMessage(defaultHint);
    setIsError(false);
    return { valid: true, numeric };
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const { valid, numeric } = validate(inputValue);

    if (!valid || numeric == null) {
      return;
    }

    if (numeric !== playerId) {
      setPlayerId(numeric);
    }

    await fetchDashboard();
  };

  return (
    <form className="player-switcher" onSubmit={handleSubmit}>
      <label className="player-switcher__label" htmlFor="player-id-input">
        Player ID
      </label>
      <input
        id="player-id-input"
        type="number"
        min={MIN_PLAYER_ID}
        value={inputValue}
        onChange={(event) => setInputValue(event.target.value)}
        onBlur={(event) => validate(event.target.value)}
        className={`player-switcher__input${isError ? ' player-switcher__input--error' : ''}`}
        placeholder="1"
      />
      <button
        type="submit"
        className="player-switcher__button"
        disabled={loading}
      >
        {loading ? 'Loading…' : 'Load'}
      </button>
      <small
        className={`player-switcher__hint${isError ? ' player-switcher__hint--error' : ''}`}
      >
        {message}
      </small>
    </form>
  );
}

export default PlayerSwitcher;
