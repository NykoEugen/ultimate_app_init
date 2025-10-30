import { useCallback, useEffect, useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import { usePlayerStore } from '../store/usePlayerStore.js';
import { apiGet, apiPost } from '../api/http.js';
import { rarityClass } from '../utils/format.js';

const slotIcons = {
  weapon: '🗡️',
  armor: '🛡️',
  helmet: '🪖',
  boots: '🥾',
  ring: '💍',
  amulet: '🪬',
  trinket: '🎖️',
  misc: '🎒',
};

const iconForSlot = (slot) => slotIcons[slot] || '🎁';

function InventoryCard({ item, onEquip, equipping }) {
  const isEquipping = equipping === item.id;
  const equipped = item.is_equipped;

  return (
    <li className={`inventory-grid__item ${equipped ? 'inventory-grid__item--equipped' : ''}`}>
      <div className="inventory-grid__icon" aria-hidden="true">
        {iconForSlot(item.slot)}
      </div>
      <div className="inventory-grid__content">
        <div className="inventory-grid__header">
          <span className="inventory-grid__name">{item.name}</span>
          <span className={rarityClass(item.rarity)}>{item.rarity}</span>
        </div>
        <div className="inventory-grid__meta">
          <span>{item.slot}</span>
          {equipped ? <span className="status-badge status-badge--success">Equipped</span> : null}
          {item.cosmetic ? (
            <span className="status-badge status-badge--accent">Cosmetic</span>
          ) : null}
        </div>
      </div>
      <button
        type="button"
        className="btn btn--secondary btn--compact"
        onClick={() => onEquip(item.id)}
        disabled={equipped || isEquipping}
      >
        {equipped ? 'Equipped' : isEquipping ? 'Equipping…' : 'Equip'}
      </button>
    </li>
  );
}

function EmptyState() {
  return (
    <div className="card card--panel">
      <h2>Inventory</h2>
      <p className="card__body">
        You have not collected any items yet. Complete quests or buy offers from the shop to fill
        your inventory.
      </p>
    </div>
  );
}

function InventoryPage() {
  const playerId = usePlayerStore((state) => state.playerId);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [equipping, setEquipping] = useState(null);
  const [error, setError] = useState(null);

  const canLoad = useMemo(() => Number.isFinite(playerId) && playerId >= 1, [playerId]);

  const loadInventory = useCallback(async () => {
    if (!canLoad) {
      setItems([]);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await apiGet(`/player/${playerId}/inventory`);
      setItems(data);
    } catch (err) {
      const message = err?.message ?? 'Failed to load inventory';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }, [canLoad, playerId]);

  useEffect(() => {
    loadInventory();
  }, [loadInventory]);

  const handleEquip = useCallback(
    async (itemId) => {
      if (!canLoad) return;
      setEquipping(itemId);
      try {
        const response = await apiPost(`/player/${playerId}/inventory/equip`, {
          item_id: itemId,
        });
        setItems(response.inventory);
        toast.success('Item equipped');
      } catch (err) {
        const message = err?.message ?? 'Failed to equip item';
        setError(message);
        toast.error(message);
      } finally {
        setEquipping(null);
      }
    },
    [canLoad, playerId],
  );

  if (!canLoad) {
    return (
      <div className="card card--panel">
        <h2>Inventory</h2>
        <p className="card__body">Set a valid player ID to view the inventory.</p>
      </div>
    );
  }

  return (
    <section className="inventory-page">
      {error ? (
        <div className="alert alert--error" role="status">
          {error}
        </div>
      ) : null}

      {loading ? (
        <div className="loader" role="status">
          Loading inventory…
        </div>
      ) : null}

      {items.length === 0 && !loading ? (
        <EmptyState />
      ) : (
        <ul className="inventory-grid">
          {items.map((item) => (
            <InventoryCard
              key={item.id}
              item={item}
              onEquip={handleEquip}
              equipping={equipping}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

export default InventoryPage;
