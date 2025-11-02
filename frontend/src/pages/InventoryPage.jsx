import { useCallback, useEffect, useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import { usePlayerStore } from '../store/usePlayerStore.js';
import { apiGet, apiPost } from '../api/http.js';
import { rarityClass } from '../utils/format.js';

const slotIcons = {
  weapon: '🗡️',
  armor: '🛡️',
  chest: '🛡️',
  back: '🎒',
  cloak: '🧥',
  head: '🪖',
  helmet: '🪖',
  shoulders: '🛡️',
  hands: '🧤',
  gloves: '🧤',
  legs: '👖',
  pants: '👖',
  feet: '🥾',
  boots: '🥾',
  neck: '📿',
  necklace: '📿',
  accessory: '📿',
  ring: '💍',
  trinket: '🎖️',
  misc: '🎒',
};

const slotLabels = {
  weapon: 'Зброя',
  armor: 'Броня',
  chest: 'Груди',
  back: 'Наплічник',
  cloak: 'Плащ',
  head: 'Голова',
  helmet: 'Шолом',
  shoulders: 'Наплічники',
  hands: 'Рукавиці',
  gloves: 'Рукавиці',
  legs: 'Штани',
  pants: 'Штани',
  feet: 'Черевики',
  boots: 'Черевики',
  neck: 'Намисто',
  necklace: 'Намисто',
  accessory: 'Аксесуар',
  ring: 'Кільце',
  trinket: 'Талісман',
  misc: 'Різне',
};

const iconForSlot = (slot) => slotIcons[slot] || '🎁';
const labelForSlot = (slot) => slotLabels[slot] || slot;

const equipmentLayout = [
  { id: 'weapon', label: 'Зброя', slots: ['weapon'], icon: '🗡️', row: 3, column: 1 },
  { id: 'ring-left', label: 'Кільце', slots: ['ring'], icon: '💍', row: 3, column: 2, slotIndex: 0 },
  { id: 'head', label: 'Голова', slots: ['head', 'helmet'], icon: '🪖', row: 1, column: 3 },
  { id: 'neck', label: 'Намисто', slots: ['neck', 'necklace', 'accessory'], icon: '📿', row: 2, column: 3 },
  { id: 'shoulders', label: 'Наплічники', slots: ['shoulders'], icon: '🛡️', row: 2, column: 2 },
  { id: 'chest', label: 'Груди', slots: ['chest', 'armor'], icon: '🛡️', row: 3, column: 3 },
  { id: 'hands', label: 'Рукавиці', slots: ['hands', 'gloves'], icon: '🧤', row: 4, column: 2 },
  { id: 'ring-right', label: 'Кільце', slots: ['ring'], icon: '💍', row: 3, column: 4, slotIndex: 1 },
  { id: 'cloak', label: 'Плащ', slots: ['cloak', 'back'], icon: '🧥', row: 2, column: 4 },
  { id: 'legs', label: 'Штани', slots: ['legs', 'pants'], icon: '👖', row: 5, column: 3 },
  { id: 'feet', label: 'Черевики', slots: ['feet', 'boots'], icon: '🥾', row: 6, column: 3 },
  { id: 'trinket', label: 'Талісман', slots: ['trinket', 'misc'], icon: '🎖️', row: 4, column: 4 },
];

function EquipmentSlot({
  layout,
  equippedItem,
  isDropTarget,
  onHover,
  onHoverMove,
  onHoverEnd,
  onContextMenu,
  onDropItem,
  onDragStart,
  onDragEnd,
  onDragEnter,
  onDragLeave,
}) {
  const { row, column } = layout;
  const filled = Boolean(equippedItem);

  const handleMouseEnter = (event) => {
    if (equippedItem) {
      onHover?.(equippedItem, layout, event);
    }
  };

  const handleMouseMove = (event) => {
    if (equippedItem) {
      onHoverMove?.(equippedItem, layout, event);
    }
  };

  const handleMouseLeave = () => {
    onHoverEnd?.();
  };

  const handleContextMenu = (event) => {
    if (!equippedItem) {
      return;
    }
    event.preventDefault();
    onContextMenu?.(equippedItem, layout, event);
  };

  const handleDragStart = (event) => {
    if (!equippedItem) {
      event.preventDefault();
      return;
    }
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData(
      'application/json',
      JSON.stringify({ itemId: equippedItem.id, source: 'slot', slot: equippedItem.slot }),
    );
    onDragStart?.(equippedItem, layout);
  };

  const handleDragOver = (event) => {
    if (event.dataTransfer.types.includes('application/json')) {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const data = event.dataTransfer.getData('application/json');
    if (!data) return;
    try {
      const parsed = JSON.parse(data);
      onDropItem?.(layout, parsed);
    } catch (err) {
      console.error('Failed to parse drag data', err);
    }
  };

  const handleDragEnter = () => {
    onDragEnter?.(layout);
  };

  const handleDragLeave = () => {
    onDragLeave?.(layout);
  };

  const handleKeyDown = (event) => {
    if (!equippedItem) {
      return;
    }
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onContextMenu?.(equippedItem, layout, event);
    }
  };

  const slotClasses = [
    'equipment-slot',
    filled ? 'equipment-slot--filled' : '',
    isDropTarget ? 'equipment-slot--droppable' : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div
      className={slotClasses}
      style={{ gridRow: row, gridColumn: column }}
      onMouseEnter={handleMouseEnter}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onContextMenu={handleContextMenu}
      draggable={filled}
      onDragStart={handleDragStart}
      onDragEnd={onDragEnd}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      tabIndex={filled ? 0 : -1}
      role={filled ? 'button' : 'presentation'}
      onKeyDown={handleKeyDown}
      aria-label={filled ? `${layout.label}: ${equippedItem.name}` : `${layout.label}: порожньо`}
    >
      <span className="equipment-slot__title">{layout.label}</span>
      <div className="equipment-slot__icon" aria-hidden="true">
        {equippedItem ? iconForSlot(equippedItem.slot) : layout.icon}
      </div>
      {equippedItem ? (
        <>
          <span className="equipment-slot__name">{equippedItem.name}</span>
          <div className="equipment-slot__tags">
            <span className={rarityClass(equippedItem.rarity)}>{equippedItem.rarity}</span>
            {equippedItem.cosmetic ? (
              <span className="status-badge status-badge--accent">Стиль</span>
            ) : null}
          </div>
        </>
      ) : (
        <span className="equipment-slot__empty">Порожньо</span>
      )}
    </div>
  );
}

function BagItem({ item, onEquip, equipping, onDragStart, onDragEnd, highlight, dim, isDragging }) {
  const isEquipping = equipping === item.id;
  const classes = [
    'inventory-bag__item',
    highlight ? 'inventory-bag__item--highlight' : '',
    dim ? 'inventory-bag__item--dim' : '',
    isDragging ? 'inventory-bag__item--dragging' : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <li
      className={classes}
      draggable
      onDragStart={(event) => {
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData(
          'application/json',
          JSON.stringify({ itemId: item.id, source: 'bag', slot: item.slot }),
        );
        onDragStart?.(item);
      }}
      onDragEnd={onDragEnd}
    >
      <div className="inventory-bag__icon" aria-hidden="true">
        {iconForSlot(item.slot)}
      </div>
      <div className="inventory-bag__content">
        <div className="inventory-bag__name">{item.name}</div>
        <div className="inventory-bag__meta">
          <span>{labelForSlot(item.slot)}</span>
          <span className={rarityClass(item.rarity)}>{item.rarity}</span>
          {item.cosmetic ? <span className="status-badge status-badge--accent">Стиль</span> : null}
        </div>
      </div>
      <button
        type="button"
        className="btn btn--secondary btn--compact"
        onClick={() => onEquip(item.id)}
        disabled={item.is_equipped || isEquipping}
      >
        {item.is_equipped ? 'Одягнено' : isEquipping ? 'Одягаємо…' : 'Одягнути'}
      </button>
    </li>
  );
}

function SlotTooltip({ tooltip }) {
  if (!tooltip) {
    return null;
  }

  const { item, layout, position } = tooltip;
  let left = position.x;
  let top = position.y;
  if (typeof window !== 'undefined') {
    left = Math.min(left, window.innerWidth - 24);
    top = Math.min(top, window.innerHeight - 24);
  }
  const style = {
    left,
    top,
  };

  return (
    <div className="inventory-tooltip" style={style} role="status">
      <header className="inventory-tooltip__header">
        <span className="inventory-tooltip__slot">{layout.label}</span>
        <span className={rarityClass(item.rarity)}>{item.rarity}</span>
      </header>
      <h3 className="inventory-tooltip__title">{item.name}</h3>
      <dl className="inventory-tooltip__stats">
        <div>
          <dt>Тип</dt>
          <dd>{labelForSlot(item.slot)}</dd>
        </div>
        <div>
          <dt>Косметичний</dt>
          <dd>{item.cosmetic ? 'Так' : 'Ні'}</dd>
        </div>
      </dl>
      <p className="inventory-tooltip__description">{item.description || 'Характеристики недоступні.'}</p>
    </div>
  );
}

function SlotContextMenu({ menu, onReplace, onUnequip, onClose, busy }) {
  if (!menu) {
    return null;
  }

  const { position, layout, item } = menu;
  const style = {
    left: position.x,
    top: position.y,
  };

  return (
    <div className="inventory-context-menu" style={style} role="menu">
      <button
        type="button"
        className="inventory-context-menu__item"
        onClick={() => {
          onReplace?.(layout);
          onClose?.();
        }}
      >
        Замінити…
      </button>
      <button
        type="button"
        className="inventory-context-menu__item"
        onClick={() => {
          onUnequip?.(item);
          onClose?.();
        }}
        disabled={busy}
      >
        Зняти
      </button>
      <button
        type="button"
        className="inventory-context-menu__item inventory-context-menu__item--muted"
        onClick={() => onClose?.()}
      >
        Закрити
      </button>
    </div>
  );
}

function InventoryPage() {
  const playerId = usePlayerStore((state) => state.playerId);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [equipping, setEquipping] = useState(null);
  const [error, setError] = useState(null);
  const [slotTooltip, setSlotTooltip] = useState(null);
  const [contextMenu, setContextMenu] = useState(null);
  const [draggedItem, setDraggedItem] = useState(null);
  const [slotDropTarget, setSlotDropTarget] = useState(null);
  const [bagDropActive, setBagDropActive] = useState(false);
  const [slotFilter, setSlotFilter] = useState(null);

  const canLoad = useMemo(() => Number.isFinite(playerId) && playerId >= 1, [playerId]);

  useEffect(() => {
    if (!contextMenu) {
      return;
    }

    const handlePointerDown = (event) => {
      if (!(event.target instanceof HTMLElement)) {
        setContextMenu(null);
        return;
      }
      if (event.target.closest('.inventory-context-menu')) {
        return;
      }
      setContextMenu(null);
    };

    window.addEventListener('pointerdown', handlePointerDown);
    return () => window.removeEventListener('pointerdown', handlePointerDown);
  }, [contextMenu]);

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
        toast.success('Предмет одягнено');
      } catch (err) {
        const message = err?.message ?? 'Не вдалося одягнути предмет';
        setError(message);
        toast.error(message);
      } finally {
        setEquipping(null);
      }
    },
    [canLoad, playerId],
  );

  const handleUnequip = useCallback(
    async (itemId) => {
      if (!canLoad) return;
      setSlotTooltip(null);
      setContextMenu(null);
      setEquipping(itemId);
      try {
        const response = await apiPost(`/player/${playerId}/inventory/unequip`, {
          item_id: itemId,
        });
        setItems(response.inventory);
        toast.success('Предмет знято');
      } catch (err) {
        const message = err?.message ?? 'Не вдалося зняти предмет';
        setError(message);
        toast.error(message);
      } finally {
        setEquipping(null);
      }
    },
    [canLoad, playerId],
  );

  const equippedBySlot = useMemo(() => {
    return items
      .filter((item) => item.is_equipped)
      .reduce((acc, item) => {
        const key = item.slot || 'misc';
        if (!acc[key]) {
          acc[key] = [];
        }
        acc[key].push(item);
        return acc;
      }, {});
  }, [items]);

  const bagItems = useMemo(
    () => items.filter((item) => !item.is_equipped),
    [items],
  );

  const equipmentSlots = useMemo(() => {
    return equipmentLayout.map((layout) => {
      const slotKeys = layout.slots ?? [];
      const equipped = slotKeys.flatMap((key) => equippedBySlot[key] || []);
      const index = Number.isInteger(layout.slotIndex) ? layout.slotIndex : 0;
      return {
        layout,
        item: equipped[index] ?? null,
      };
    });
  }, [equippedBySlot]);

  const showSlotTooltip = useCallback((item, layout, event) => {
    const position = {
      x: event.clientX + 16,
      y: event.clientY + 16,
    };
    setSlotTooltip({ item, layout, position });
  }, []);

  const updateSlotTooltip = useCallback((item, layout, event) => {
    setSlotTooltip((current) => {
      if (!current) {
        return current;
      }
      return {
        item,
        layout,
        position: {
          x: event.clientX + 16,
          y: event.clientY + 16,
        },
      };
    });
  }, []);

  const hideSlotTooltip = useCallback(() => {
    setSlotTooltip(null);
  }, []);

  const openSlotContextMenu = useCallback((item, layout, event) => {
    setSlotTooltip(null);
    const position = {
      x: event.clientX,
      y: event.clientY,
    };
    setContextMenu({ item, layout, position });
  }, []);

  const closeSlotContextMenu = useCallback(() => {
    setContextMenu(null);
  }, []);

  const handleReplaceRequest = useCallback((layout) => {
    setSlotFilter(layout.slots ?? []);
  }, []);

  const handleBagFilterClear = useCallback(() => {
    setSlotFilter(null);
  }, []);

  const resetDragState = useCallback(() => {
    setDraggedItem(null);
    setSlotDropTarget(null);
    setBagDropActive(false);
  }, []);

  const handleSlotDragStart = useCallback(
    (item, layout) => {
      setDraggedItem({ id: item.id, source: 'slot', slot: item.slot, layoutId: layout.id });
      setSlotTooltip(null);
      setContextMenu(null);
    },
    [],
  );

  const handleBagDragStart = useCallback((item) => {
    setDraggedItem({ id: item.id, source: 'bag', slot: item.slot });
    setContextMenu(null);
  }, []);

  const handleDragEnd = useCallback(() => {
    resetDragState();
  }, [resetDragState]);

  const handleSlotDragEnter = useCallback(
    (layout) => {
      if (draggedItem?.source === 'bag') {
        setSlotDropTarget(layout.id);
      }
    },
    [draggedItem],
  );

  const handleSlotDragLeave = useCallback((layout) => {
    setSlotDropTarget((current) => (current === layout.id ? null : current));
  }, []);

  const handleSlotDrop = useCallback(
    (layout, data) => {
      if (draggedItem?.source === 'bag') {
        handleEquip(draggedItem.id);
      } else if (data?.source === 'bag' && Number.isInteger(data.itemId)) {
        handleEquip(Number(data.itemId));
      }
      resetDragState();
      setSlotFilter(null);
    },
    [draggedItem, handleEquip, resetDragState],
  );

  const handleBagDragEnter = useCallback((event) => {
    if (draggedItem?.source === 'slot') {
      setBagDropActive(true);
    }
    if (event?.preventDefault) {
      event.preventDefault();
    }
  }, [draggedItem]);

  const handleBagDragLeave = useCallback((event) => {
    if (event?.relatedTarget instanceof HTMLElement) {
      if (event.currentTarget.contains(event.relatedTarget)) {
        return;
      }
    }
    setBagDropActive(false);
  }, []);

  const handleBagDrop = useCallback(
    (data) => {
      if (draggedItem?.source === 'slot') {
        handleUnequip(draggedItem.id);
      } else if (data?.source === 'slot' && Number.isInteger(data.itemId)) {
        handleUnequip(Number(data.itemId));
      }
      resetDragState();
    },
    [draggedItem, handleUnequip, resetDragState],
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
          Завантаження інвентаря…
        </div>
      ) : null}

      <div className="inventory-layout">
        <div className="card card--panel equipment-card">
          <h2>Екіпірування</h2>
          <div className="equipment-grid">
            <div className="equipment-figure" aria-hidden="true" />
            {equipmentSlots.map(({ layout, item }) => (
              <EquipmentSlot
                key={layout.id}
                layout={layout}
                equippedItem={item}
                isDropTarget={slotDropTarget === layout.id}
                onHover={showSlotTooltip}
                onHoverMove={updateSlotTooltip}
                onHoverEnd={hideSlotTooltip}
                onContextMenu={openSlotContextMenu}
                onDropItem={handleSlotDrop}
                onDragStart={handleSlotDragStart}
                onDragEnd={handleDragEnd}
                onDragEnter={handleSlotDragEnter}
                onDragLeave={handleSlotDragLeave}
              />
            ))}
          </div>
        </div>
        <div
          className={`card card--panel inventory-bag ${bagDropActive ? 'inventory-bag--droppable' : ''}`.trim()}
          onDragOver={(event) => {
            if (event.dataTransfer.types.includes('application/json')) {
              event.preventDefault();
              event.dataTransfer.dropEffect = 'move';
            }
          }}
          onDragEnter={handleBagDragEnter}
          onDragLeave={handleBagDragLeave}
          onDrop={(event) => {
            event.preventDefault();
            let data = null;
            const payload = event.dataTransfer.getData('application/json');
            if (payload) {
              try {
                data = JSON.parse(payload);
              } catch (err) {
                console.error('Failed to parse drag payload', err);
              }
            }
            handleBagDrop(data);
          }}
        >
          <div className="inventory-bag__header">
            <h2>Сумка</h2>
            <span className="inventory-bag__counter">
              {bagItems.length}/{items.length}
            </span>
            {slotFilter ? (
              <button
                type="button"
                className="inventory-bag__clear-filter"
                onClick={handleBagFilterClear}
              >
                Скинути відбір
              </button>
            ) : null}
          </div>
          {bagItems.length === 0 ? (
            <p className="inventory-bag__empty">
              У сумці поки що пусто. Вирушай у пригоди або заглянь до крамниці.
            </p>
          ) : (
            <ul className="inventory-bag__grid">
              {bagItems.map((item) => {
                const matchesFilter = slotFilter ? slotFilter.includes(item.slot) : false;
                return (
                  <BagItem
                    key={item.id}
                    item={item}
                    onEquip={handleEquip}
                    equipping={equipping}
                    onDragStart={handleBagDragStart}
                    onDragEnd={handleDragEnd}
                    highlight={slotFilter ? matchesFilter : draggedItem?.source === 'bag' && draggedItem.id === item.id}
                    dim={Boolean(slotFilter) && !matchesFilter}
                    isDragging={draggedItem?.id === item.id}
                  />
                );
              })}
            </ul>
          )}
        </div>
      </div>
      <SlotTooltip tooltip={slotTooltip} />
      <SlotContextMenu
        menu={contextMenu}
        onReplace={handleReplaceRequest}
        onUnequip={(item) => handleUnequip(item.id)}
        onClose={closeSlotContextMenu}
        busy={Boolean(equipping)}
      />
    </section>
  );
}

export default InventoryPage;
