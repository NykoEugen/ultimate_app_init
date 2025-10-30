import { useCallback, useEffect, useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import { usePlayerStore } from '../store/usePlayerStore.js';
import { apiGet, apiPost } from '../api/http.js';
import { rarityClass } from '../utils/format.js';

const rarityIcons = {
  common: '🎁',
  uncommon: '🧪',
  rare: '🔮',
  epic: '✨',
  legendary: '💎',
  seasonal: '🎉',
};

const iconForOffer = (offer) => {
  if (offer.icon && /\p{Extended_Pictographic}/u.test(offer.icon)) {
    return offer.icon;
  }
  return rarityIcons[offer.rarity] || '🛒';
};

function parseEffects(description) {
  const effects = {
    bonuses: [],
    penalties: [],
    notes: [],
  };

  if (!description) {
    return effects;
  }

  const segments = description.split(/[\n;]+/);
  segments.forEach((segment) => {
    const text = segment.trim();
    if (!text) {
      return;
    }

    if (text.startsWith('-') || /debuff|penalty|reduce|minus/i.test(text)) {
      effects.penalties.push(text.replace(/^[\-\s]*/, '').trim());
    } else if (text.startsWith('+') || /buff|bonus|increase|plus|gain/i.test(text)) {
      effects.bonuses.push(text.replace(/^[+\s]*/, '').trim());
    } else {
      effects.notes.push(text);
    }
  });

  return effects;
}

function WalletSummary({ wallet }) {
  if (!wallet) return null;
  return (
    <div className="wallet-summary">
      <div className="wallet-summary__item">
        <span aria-hidden="true">🪙</span>
        <span>
          Gold <strong>{wallet.gold}</strong>
        </span>
      </div>
      <div className="wallet-summary__item">
        <span aria-hidden="true">💎</span>
        <span>
          Gems <strong>{wallet.gems}</strong>
        </span>
      </div>
    </div>
  );
}

function OfferCard({ offer, onBuy, buying }) {
  const isBuying = buying === offer.id;
  const { bonuses, penalties, notes } = parseEffects(offer.description);
  return (
    <li className="shop-grid__item">
      <div className="shop-grid__icon" aria-hidden="true">
        {iconForOffer(offer)}
      </div>
      <div className="shop-grid__content">
        <h3>{offer.name}</h3>
        <div className="shop-grid__tags">
          <span className={rarityClass(offer.rarity)}>{offer.rarity}</span>
          <span className="shop-tag">{offer.cosmetic ? 'Cosmetic' : `Slot: ${offer.slot}`}</span>
          {offer.isLimited ? <span className="shop-tag shop-tag--limited">Limited</span> : null}
          {offer.owned ? <span className="shop-tag shop-tag--owned">Owned</span> : null}
        </div>
        {bonuses.length ? (
          <div className="shop-grid__effects shop-grid__effects--bonus">
            <strong>Bonuses</strong>
            <ul>
              {bonuses.map((line, index) => (
                <li key={`bonus-${offer.id}-${index}`}>+ {line}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {penalties.length ? (
          <div className="shop-grid__effects shop-grid__effects--penalty">
            <strong>Debuffs</strong>
            <ul>
              {penalties.map((line, index) => (
                <li key={`penalty-${offer.id}-${index}`}>- {line}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {notes.length ? (
          <div className="shop-grid__description">
            {notes.map((line, index) => (
              <p key={`note-${offer.id}-${index}`}>{line}</p>
            ))}
          </div>
        ) : null}
        {!bonuses.length && !penalties.length && !notes.length && offer.description ? (
          <p className="shop-grid__description">{offer.description}</p>
        ) : null}
        <div className="shop-grid__meta">
          <span>
            Cost: <strong>{offer.priceGold}</strong> gold
          </span>
          {offer.isLimited && offer.limitInfo ? <span>{offer.limitInfo}</span> : null}
        </div>
      </div>
      <button
        type="button"
        className="btn btn--primary btn--compact"
        onClick={() => onBuy(offer.id)}
        disabled={isBuying}
      >
        {isBuying ? 'Purchasing…' : 'Buy'}
      </button>
    </li>
  );
}

function normalizeOffer(raw) {
  const normalized = {
    id: raw.offer_id ?? raw.id,
    name: raw.item_name ?? raw.title ?? 'Mystery Item',
    description: raw.description ?? '',
    rarity: (raw.rarity ?? 'common')?.toLowerCase(),
    priceGold: raw.price_gold ?? raw.cost_gold ?? 0,
    isLimited: raw.is_limited ?? Boolean(raw.limit_per_player),
    owned: raw.owned ?? false,
    slot: raw.slot ?? 'misc',
    cosmetic: raw.cosmetic ?? false,
    icon: raw.icon ?? null,
  };

  if (raw.limit_per_player) {
    normalized.limitInfo = `Limit ${raw.limit_per_player} per player`;
  }

  return normalized;
}
function ShopPage() {
  const playerId = usePlayerStore((state) => state.playerId);
  const [wallet, setWallet] = useState(null);
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [buying, setBuying] = useState(null);
  const [error, setError] = useState(null);

  const canLoad = useMemo(() => Number.isFinite(playerId) && playerId >= 1, [playerId]);

  const loadShop = useCallback(async () => {
    if (!canLoad) {
      setWallet(null);
      setOffers([]);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await apiGet(`/player/${playerId}/shop`);
      setWallet(data.wallet);
      const normalizedOffers = (data.offers ?? []).map(normalizeOffer);
      setOffers(normalizedOffers);
    } catch (err) {
      const message = err?.message ?? 'Failed to load shop';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }, [canLoad, playerId]);

  useEffect(() => {
    loadShop();
  }, [loadShop]);

  const handleBuy = useCallback(
    async (offerId) => {
      if (!canLoad) return;
      setBuying(offerId);
      try {
        const result = await apiPost(`/player/${playerId}/shop/buy`, { offer_id: offerId });
        setWallet(result.wallet);
        toast.success('Purchase complete');
        await loadShop();
      } catch (err) {
        let message = err?.message ?? 'Purchase failed';

        const normalizeDetails = () => {
          if (!err?.details) {
            return null;
          }

          try {
            const parsed = JSON.parse(err.details);
            if (parsed?.detail) {
              return String(parsed.detail);
            }
          } catch (parseError) {
            // ignore json parse errors
          }

          return String(err.details);
        };

        const details = normalizeDetails();
        if (typeof details === 'string' && details.trim()) {
          message = details.trim();
        }

        if (err?.status === 402 || /not enough gold/i.test(message)) {
          message = 'Not enough gold to complete this purchase. Earn more gold and try again.';
        }

        setError(message);
        toast.error(message);
      } finally {
        setBuying(null);
      }
    },
    [canLoad, playerId, loadShop],
  );

  if (!canLoad) {
    return (
      <div className="card card--panel">
        <h2>Shop</h2>
        <p className="card__body">Set a valid player ID to view shop offers.</p>
      </div>
    );
  }

  return (
    <section className="shop-page">
      {error ? (
        <div className="alert alert--error" role="status">
          {error}
        </div>
      ) : null}

      <WalletSummary wallet={wallet} />

      {loading ? (
        <div className="loader" role="status">
          Loading offers…
        </div>
      ) : null}

      {offers.length ? (
        <ul className="shop-grid">
          {offers.map((offer) => (
            <OfferCard key={offer.id} offer={offer} onBuy={handleBuy} buying={buying} />
          ))}
        </ul>
      ) : (
        !loading && (
          <div className="card card--panel">
            <h2>Shop</h2>
            <p className="card__body">No offers available right now. Check back soon!</p>
          </div>
        )
      )}
    </section>
  );
}

export default ShopPage;
