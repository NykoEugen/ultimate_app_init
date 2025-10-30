import { useEffect, useMemo, useRef } from 'react';
import toast from 'react-hot-toast';
import { usePlayerStore } from '../store/usePlayerStore.js';
import { formatSecondsToHMS, rarityClass } from '../utils/format.js';

function ProgressBar({ value, max }) {
  const safeMax = max > 0 ? max : 1;
  const percent = Math.min(100, Math.round((value / safeMax) * 100));

  return (
    <div className="progress" aria-valuemin={0} aria-valuemax={safeMax} aria-valuenow={value}>
      <div className="progress__bar" style={{ width: `${percent}%` }} />
    </div>
  );
}

function StatusBadge({ children, tone = 'info' }) {
  return <span className={`status-badge status-badge--${tone}`}>{children}</span>;
}

function PlayerHeader({ player, pending }) {
  if (!player) {
    return null;
  }

  const xpNeeded = player.xp_to_next_level ?? 0;
  const xpProgressMax = player.xp + xpNeeded;

  return (
    <section className="card card--panel player-header">
      <header className="card__header">
        <div>
          <h2>{player.username}</h2>
          <p className="card__meta">ID: {player.id}</p>
        </div>
        <div className="player-header__level">
          <span className="player-header__level-label">Level</span>
          <span className="player-header__level-value">{player.level}</span>
        </div>
      </header>

      <div className="player-header__stats">
        <div>
          <span className="player-header__stat-label">XP Progress</span>
          <span className="player-header__stat-value">
            {player.xp} / {xpProgressMax}
          </span>
          <ProgressBar value={player.xp} max={xpProgressMax} />
        </div>
        <div>
          <span className="player-header__stat-label">Energy</span>
          <span className="player-header__stat-value">
            {player.energy} / {player.max_energy}
          </span>
          <ProgressBar value={player.energy} max={player.max_energy || 1} />
        </div>
      </div>

      <div className="player-header__badges">
        {pending?.you_have_unspent_points ? (
          <StatusBadge tone="warning">Max energy reached</StatusBadge>
        ) : null}
        {pending?.you_can_equip_new_item ? (
          <StatusBadge tone="accent">New gear available</StatusBadge>
        ) : null}
      </div>
    </section>
  );
}

function DailyRewardCard({ daily, loading, onClaim }) {
  if (!daily) {
    return null;
  }

  const handleClaim = async () => {
    if (daily.can_claim && !loading) {
      await onClaim();
    }
  };

  return (
    <section className="card card--panel">
      <div className="card__header">
        <h2>Daily Reward</h2>
        <StatusBadge tone={daily.can_claim ? 'success' : 'muted'}>
          {daily.can_claim ? 'Available now' : 'On cooldown'}
        </StatusBadge>
      </div>
      <p className="card__body">
        Claim your daily reward to keep momentum. Rewards include XP and energy boosts.
      </p>

      <ul className="card__list">
        <li>XP: +{daily.preview_reward?.xp ?? 0}</li>
        <li>Energy: +{daily.preview_reward?.energy ?? 0}</li>
      </ul>

      {!daily.can_claim ? (
        <p className="card__hint">
          Ready in {formatSecondsToHMS(daily.cooldown_seconds_left ?? 0)}
        </p>
      ) : null}

      <button
        type="button"
        className="btn btn--primary"
        onClick={handleClaim}
        disabled={!daily.can_claim || loading}
      >
        {loading ? 'Processing…' : 'Claim Daily Reward'}
      </button>
    </section>
  );
}

function QuestCard({ quest, loading, onChoose }) {
  if (!quest) {
    return null;
  }

  const hasChoices = Array.isArray(quest.choices) && quest.choices.length > 0;

  return (
    <section className="card card--panel">
      <div className="card__header">
        <div>
          <h2>{quest.title}</h2>
          <p className="card__meta">{quest.is_final ? 'Final stage' : 'In progress'}</p>
        </div>
        <StatusBadge tone="info">Quest</StatusBadge>
      </div>
      <p className="card__body">{quest.body}</p>

      {hasChoices ? (
        <div className="quest-choices">
          {quest.choices.map((choice) => (
            <div key={choice.choice_id} className="quest-choice">
              <div>
                <strong>{choice.label}</strong>
                <p className="quest-choice__reward">
                  Reward: +{choice.reward_preview?.xp ?? choice.reward_xp ?? 0} XP{' '}
                  {choice.reward_preview?.item_name
                    ? `• ${choice.reward_preview.item_name}`
                    : ''}
                </p>
              </div>
              <button
                type="button"
                className="btn btn--secondary"
                onClick={() => onChoose(choice.choice_id)}
                disabled={loading}
              >
                {loading ? 'Processing…' : 'Choose'}
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p className="card__hint">New quest steps will appear soon. Check back later.</p>
      )}
    </section>
  );
}

function InventoryStrip({ items }) {
  return (
    <section className="card card--panel">
      <div className="card__header">
        <h2>Quick Inventory</h2>
        <StatusBadge tone="muted">{items?.length ? `${items.length} items` : 'Empty'}</StatusBadge>
      </div>

      {items?.length ? (
        <ul className="inventory-strip">
          {items.map((item) => (
            <li key={item.id} className="inventory-strip__item">
              <div className="inventory-strip__name">
                {item.name}
                <span className={rarityClass(item.rarity)}>{item.rarity}</span>
              </div>
              <div className="inventory-strip__meta">
                <span>{item.slot}</span>
                {item.is_equipped ? <StatusBadge tone="success">Equipped</StatusBadge> : null}
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="card__hint">Collect gear from quests and rewards to fill your inventory.</p>
      )}
    </section>
  );
}

function MilestoneCard({ milestone }) {
  if (!milestone) {
    return null;
  }

  const progressMax = milestone.target || 1;
  const progressValue = Math.min(progressMax, milestone.current || 0);

  return (
    <section className="card card--panel">
      <div className="card__header">
        <h2>Milestone</h2>
        <StatusBadge tone="accent">{milestone.label}</StatusBadge>
      </div>
      <p className="card__body">Stay on track to unlock exclusive rewards.</p>
      <ProgressBar value={progressValue} max={progressMax} />
      <p className="card__meta">
        Progress {progressValue} / {progressMax}
      </p>
      <p className="card__hint">Upcoming reward: {milestone.reward_preview}</p>
    </section>
  );
}

function DashboardEmptyState() {
  return (
    <div className="card card--panel">
      <h2>Dashboard</h2>
      <p className="card__body">
        Player data will appear here after the first fetch. Use the player switcher to load a profile.
      </p>
    </div>
  );
}

function DashboardPage() {
  const fetchDashboard = usePlayerStore((state) => state.fetchDashboard);
  const claimDaily = usePlayerStore((state) => state.claimDaily);
  const chooseQuestOption = usePlayerStore((state) => state.choose);

  const dashboard = usePlayerStore((state) => state.dashboard);
  const loadingDashboard = usePlayerStore((state) => state.loadingDashboard);
  const error = usePlayerStore((state) => state.error);
  const playerId = usePlayerStore((state) => state.playerId);

  const lastErrorRef = useRef();

  useEffect(() => {
    if (Number.isFinite(playerId) && !dashboard) {
      fetchDashboard();
    }
  }, [playerId, dashboard, fetchDashboard]);

  const alertMessage = useMemo(() => error, [error]);

  useEffect(() => {
    if (error && error !== lastErrorRef.current) {
      toast.error(error);
      lastErrorRef.current = error;
    }

    if (!error) {
      lastErrorRef.current = undefined;
    }
  }, [error]);

  return (
    <div className="dashboard-page">
      {alertMessage ? (
        <div className="alert alert--error" role="status">
          {alertMessage}
        </div>
      ) : null}

      {loadingDashboard && (
        <div className="loader" role="status" aria-live="polite">
          Loading dashboard…
        </div>
      )}

      {dashboard ? (
        <>
          <PlayerHeader player={dashboard.player} pending={dashboard.pending_actions} />
          <DailyRewardCard
            daily={dashboard.daily}
            loading={loadingDashboard}
            onClaim={claimDaily}
          />
          <QuestCard
            quest={dashboard.quest}
            loading={loadingDashboard}
            onChoose={chooseQuestOption}
          />
          <InventoryStrip items={dashboard.inventory_preview} />
          <MilestoneCard milestone={dashboard.milestone} />
        </>
      ) : (
        !loadingDashboard && <DashboardEmptyState />
      )}
    </div>
  );
}

export default DashboardPage;
