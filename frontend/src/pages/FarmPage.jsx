import { useCallback, useEffect, useMemo } from 'react';
import toast from 'react-hot-toast';
import { usePlayerStore } from '../store/usePlayerStore.js';
import { useFarmStore } from '../store/useFarmStore.js';
import { formatSecondsToHMS } from '../utils/format.js';

const PLANT_ICON_MAP = {
  plant_carrot_common: '🥕',
  plant_starverbena_uncommon: '✨',
  plant_strawberry_rare: '🍓',
  plant_pumpkin_gloria: '🎃',
  plant_lavender_epic: '💜',
};

const resolvePlantIcon = (icon) => {
  if (!icon) {
    return '🌱';
  }
  return PLANT_ICON_MAP[icon] ?? icon;
};

function ProgressBar({ value = 0, max = 100, label }) {
  const safeMax = max > 0 ? max : 1;
  const percent = Math.min(100, Math.max(0, Math.round((value / safeMax) * 100)));
  return (
    <div className="farm-progress">
      <div className="farm-progress__label">
        {label}
        <span>{percent}%</span>
      </div>
      <div className="farm-progress__track">
        <div className="farm-progress__value" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

function PlantActionList({ plants, onSelect, disabled, availableGold, starterSeeds }) {
  if (!plants?.length) {
    return <p className="farm-empty-hint">Немає доступних культур для посадки.</p>;
  }

  return (
    <div className="farm-plant-actions">
      {plants.map((plant) => (
        <button
          type="button"
          key={plant.id}
          className={`farm-plant-actions__item${plant.is_unlocked ? '' : ' farm-plant-actions__item--locked'}`}
          onClick={() => onSelect(plant)}
          disabled={disabled || !plant.is_unlocked || (plant.seed_cost > availableGold && starterSeeds <= 0)}
        >
          <div className="farm-plant-actions__icon" aria-hidden="true">
            {resolvePlantIcon(plant.icon)}
          </div>
          <div>
            <strong>{plant.name}</strong>
            <p>{plant.energy_cost} ⚡</p>
            <div className="farm-plant-actions__meta">
              <span>
                {plant.seed_cost} <span aria-hidden="true">🪙</span>
              </span>
              {!plant.is_unlocked ? (
                <span className="farm-plant-actions__tag farm-plant-actions__tag--locked">Заблоковано</span>
              ) : plant.seed_cost > availableGold ? (
                <span className="farm-plant-actions__tag farm-plant-actions__tag--warn">Бракує золота</span>
              ) : starterSeeds > 0 && plant.seed_cost > 0 ? (
                <span className="farm-plant-actions__tag">Подарункове насіння</span>
              ) : null}
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}

function PlotCard({
  plot,
  plants,
  onPlant,
  onHarvest,
  onUnlock,
  disabled,
  now,
  availableGold,
  starterSeeds,
}) {
  const handlePlant = useCallback(
    (plant) => {
      onPlant(plot.id, plant.id);
    },
    [onPlant, plot.id],
  );

  const remainingLabel = useMemo(() => {
    if (!plot.crop) return null;
    const readyAt = new Date(plot.crop.ready_at);
    const diffSeconds = Math.floor((readyAt.getTime() - now) / 1000);
    if (diffSeconds <= 0 || plot.crop.state === 'ready') {
      return 'Готово до збору';
    }
    return `Готово через ${formatSecondsToHMS(diffSeconds)}`;
  }, [plot.crop, now]);

  if (!plot.unlocked) {
    return (
      <div className="farm-plot farm-plot--locked">
        <div className="farm-plot__header">
          <h3>Ділянка #{plot.slot_index}</h3>
          <span className="farm-plot__status">Закрито</span>
        </div>
        <p className="farm-plot__hint">
          Потрібен рівень героя {plot.unlock_level_requirement} та фермерства{' '}
          {plot.unlock_farming_level_requirement}.
        </p>
        <button
          type="button"
          className="btn btn--primary"
          onClick={() => onUnlock(plot.id)}
          disabled={disabled}
        >
          Відкрити за {plot.unlock_cost} 🪙
        </button>
      </div>
    );
  }

  return (
    <div className="farm-plot">
      <div className="farm-plot__header">
        <h3>Ділянка #{plot.slot_index}</h3>
        <span className={`farm-plot__status farm-plot__status--${plot.crop ? plot.crop.state : 'empty'}`}>
          {plot.crop
            ? plot.crop.state === 'ready'
              ? 'Готово'
              : 'Росте'
            : 'Вільна'}
        </span>
      </div>
      {plot.crop ? (
        <>
          <div className="farm-plot__crop">
            <div className="farm-plot__crop-icon" aria-hidden="true">
              {resolvePlantIcon(plot.crop.plant_type.icon)}
            </div>
            <div>
              <strong>{plot.crop.plant_type.name}</strong>
              <p>{remainingLabel}</p>
            </div>
          </div>
          <button
            type="button"
            className="btn btn--primary"
            onClick={() => onHarvest(plot.id)}
            disabled={disabled || plot.crop.state !== 'ready'}
          >
            Зібрати врожай
          </button>
        </>
      ) : (
        <>
          <p className="farm-plot__hint">Оберіть, що посадити:</p>
          <PlantActionList
            plants={plants}
            onSelect={handlePlant}
            disabled={disabled}
            availableGold={availableGold}
            starterSeeds={starterSeeds}
          />
        </>
      )}
    </div>
  );
}

function PlantCard({ plant }) {
  const growthHours = Math.round((plant.growth_seconds / 3600) * 10) / 10;
  return (
    <li className="farm-catalog__item">
      <div className="farm-catalog__icon" aria-hidden="true">
        {resolvePlantIcon(plant.icon)}
      </div>
      <div className="farm-catalog__content">
        <h3>{plant.name}</h3>
        <p className="farm-catalog__meta">
          {plant.energy_cost} ⚡ · {plant.seed_cost} 🪙 · {plant.xp_reward} XP
        </p>
        <p className="farm-catalog__description">{plant.description}</p>
        <div className="farm-catalog__tags">
          <span>Готовність ≈ {growthHours} год.</span>
          <span>Вимога рівня героя {plant.unlock_level}</span>
          <span>Рівень фермерства {plant.unlock_farming_level}</span>
          <span className={`farm-catalog__badge ${plant.is_unlocked ? '' : 'farm-catalog__badge--locked'}`}>
            {plant.is_unlocked ? 'Доступно' : 'Недоступно'}
          </span>
        </div>
      </div>
    </li>
  );
}

function FarmPage() {
  const playerId = usePlayerStore((state) => state.playerId);
  const {
    farm,
    loading,
    action,
    error,
    fetchFarm,
    plantCrop,
    harvestCrop,
    unlockPlot,
    upgradeTool,
    refillEnergy,
    reset,
  } = useFarmStore();

  const actionDisabled = Boolean(action);
  const now = useMemo(() => Date.now(), [farm?.player_id, action]);
  const walletGold = farm?.wallet_gold ?? 0;

  useEffect(() => {
    if (Number.isFinite(playerId)) {
      fetchFarm(playerId).catch((err) => {
        toast.error(err?.message ?? 'Не вдалося завантажити ферму.');
      });
    } else {
      reset();
    }
  }, [playerId, fetchFarm, reset]);

  const handlePlant = useCallback(
    async (plotId, plantId) => {
      try {
        const response = await plantCrop(playerId, plotId, plantId);
        toast.success(response.message);
      } catch (err) {
        toast.error(err?.message ?? 'Помилка посадки.');
      }
    },
    [plantCrop, playerId],
  );

  const handleHarvest = useCallback(
    async (plotId) => {
      try {
        const response = await harvestCrop(playerId, plotId);
        toast.success(response.message);
      } catch (err) {
        toast.error(err?.message ?? 'Помилка збору врожаю.');
      }
    },
    [harvestCrop, playerId],
  );

  const handleUnlock = useCallback(
    async (plotId) => {
      try {
        const response = await unlockPlot(playerId, plotId);
        toast.success(response.message);
      } catch (err) {
        toast.error(err?.message ?? 'Не вдалося відкрити ділянку.');
      }
    },
    [unlockPlot, playerId],
  );

  const handleUpgradeTool = useCallback(async () => {
    try {
      const response = await upgradeTool(playerId);
      toast.success(response.message);
    } catch (err) {
      toast.error(err?.message ?? 'Не вдалося покращити інструмент.');
    }
  }, [upgradeTool, playerId]);

  const handleRefill = useCallback(
    async (amount) => {
      if (!farm?.stats) return;
      const diff = amount === 'full' ? farm.stats.max_energy - farm.stats.energy : amount;
      if (!diff || diff <= 0) {
        toast('Енергія вже на максимумі.');
        return;
      }
      try {
        const response = await refillEnergy(playerId, diff);
        toast.success(response.message);
      } catch (err) {
        toast.error(err?.message ?? 'Не вдалося поповнити енергію.');
      }
    },
    [refillEnergy, playerId, farm?.stats],
  );

  const handleRefresh = useCallback(() => {
    if (!Number.isFinite(playerId)) return;
    fetchFarm(playerId).catch((err) => {
      toast.error(err?.message ?? 'Не вдалося оновити ферму.');
    });
  }, [fetchFarm, playerId]);

  if (!Number.isFinite(playerId)) {
    return <p>Оберіть гравця, щоб побачити ферму.</p>;
  }

  if (loading && !farm) {
    return <p>Завантаження ферми…</p>;
  }

  const plots = farm?.plots ?? [];
  const plants = farm?.available_plants ?? [];
  const stats = farm?.stats;
  const starterSeeds = stats?.starter_seed_charges ?? 0;

  return (
    <div className="farm-page">
      <header className="farm-header">
        <div className="farm-stat-card">
          <h2>Рівень ферми</h2>
          <div className="farm-stat-card__value">{stats?.level ?? 1}</div>
          <ProgressBar
            value={stats?.xp ?? 0}
            max={(stats?.xp_to_next_level ?? 1) || 1}
            label={`${stats?.xp ?? 0} / ${stats?.xp_to_next_level ?? 0} XP`}
          />
        </div>
        <div className="farm-stat-card">
          <h2>Енергія</h2>
          <div className="farm-stat-card__value">
            {stats?.energy ?? 0}/{stats?.max_energy ?? 0} ⚡
          </div>
          <div className="farm-actions">
            <button
              type="button"
              className="btn btn--secondary"
              onClick={() => handleRefill(10)}
              disabled={actionDisabled}
            >
              +10 за золото
            </button>
            <button
              type="button"
              className="btn btn--secondary"
              onClick={() => handleRefill('full')}
              disabled={actionDisabled}
            >
              До максимуму
            </button>
          </div>
        </div>
        <div className="farm-stat-card">
          <h2>Золото ферми</h2>
          <div className="farm-stat-card__value farm-stat-card__value--inline">
            <span aria-hidden="true">🪙</span>
            <span>{walletGold}</span>
          </div>
          <p className="farm-stat-card__hint">
            Необхідне для насіння та нових ділянок. Подарункових насінин: {starterSeeds}
          </p>
        </div>
        <div className="farm-stat-card">
          <h2>Інструмент</h2>
          <div className="farm-stat-card__value">{stats?.tool?.name ?? '—'}</div>
          <p className="farm-stat-card__hint">
            Бонус швидкості: {stats?.tool?.bonus_percent ?? 0}%
          </p>
          <button
            type="button"
            className="btn btn--primary"
            onClick={handleUpgradeTool}
            disabled={actionDisabled}
          >
            Покращити інструмент
          </button>
        </div>
      </header>

      <section className="farm-panel">
        <div className="farm-panel__header">
          <div>
            <h2>Ділянки</h2>
            <p className="farm-panel__hint">
              Обирайте рослини, щоб зростати у спокійному темпі. Гра навмисне казуальна — жодних
              штрафів за експерименти.
            </p>
          </div>
          <div className="farm-panel__actions">
            <button type="button" className="btn btn--secondary" onClick={handleRefresh} disabled={loading}>
              Оновити
            </button>
          </div>
        </div>
        {error ? <div className="farm-alert">{error}</div> : null}
        <div className="farm-plots-grid">
          {plots.map((plot) => (
            <PlotCard
              key={plot.id}
              plot={plot}
              plants={plants}
              onPlant={handlePlant}
              onHarvest={handleHarvest}
              onUnlock={handleUnlock}
              disabled={actionDisabled}
              now={now}
              availableGold={walletGold}
              starterSeeds={starterSeeds}
            />
          ))}
        </div>
      </section>

      <section className="farm-panel">
        <div className="farm-panel__header">
          <div>
            <h2>Каталог культур</h2>
            <p className="farm-panel__hint">Нові рослини відкриваються із зростанням рівня героя та ферми.</p>
          </div>
        </div>
        <ul className="farm-catalog">
          {plants.map((plant) => (
            <PlantCard key={plant.id} plant={plant} />
          ))}
        </ul>
      </section>
    </div>
  );
}

export default FarmPage;
