import { useEffect, useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import { apiGet, apiPost, apiPut } from '../api/http.js';

const rarityOptions = ['common', 'uncommon', 'rare', 'epic', 'legendary', 'seasonal'];

const createEquipmentForm = () => ({
  name: '',
  slot: '',
  rarity: 'common',
  cosmetic: false,
  description: '',
  icon: '',
});

const createPlantForm = () => ({
  name: '',
  description: '',
  growth_seconds: '600',
  xp_reward: '15',
  energy_cost: '2',
  seed_cost: '0',
  sell_price: '0',
  unlock_level: '1',
  unlock_farming_level: '1',
  icon: '',
});

const createEmptyChoice = () => ({
  id: '',
  label: '',
  next_node_id: '',
  reward_xp: '0',
  reward_item_id: '',
});

const createEmptyNode = ({ isStart = false, isFinal = false } = {}) => ({
  id: '',
  title: '',
  body: '',
  is_start: isStart,
  is_final: isFinal,
  choices: [],
});

const createQuestForm = () => ({
  title: '',
  description: '',
  is_repeatable: false,
  nodes: [createEmptyNode({ isStart: true, isFinal: true })],
});

function AdminPage() {
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  const [equipmentForm, setEquipmentForm] = useState(createEquipmentForm);
  const [plantForm, setPlantForm] = useState(createPlantForm);
  const [questForm, setQuestForm] = useState(createQuestForm);

  const [equipmentItems, setEquipmentItems] = useState([]);
  const [plants, setPlants] = useState([]);
  const [quests, setQuests] = useState([]);
  const [editingEquipmentId, setEditingEquipmentId] = useState(null);
  const [editingPlantId, setEditingPlantId] = useState(null);
  const [editingQuestId, setEditingQuestId] = useState(null);

  const toInputString = (value, fallback = '') => (value == null ? fallback : String(value));

  useEffect(() => {
    let cancelled = false;
    async function loadAdminData() {
      try {
        const [equipment, plantCatalog, questList] = await Promise.all([
          apiGet('/admin/equipment'),
          apiGet('/admin/plants'),
          apiGet('/admin/quests'),
        ]);
        if (!cancelled) {
          setEquipmentItems(equipment);
          setPlants(plantCatalog);
          setQuests(questList);
          setLoadError(null);
        }
      } catch (error) {
        if (!cancelled) {
          const message = error?.details || error?.message || 'Не вдалося завантажити дані адміністрування.';
          setLoadError(message);
          toast.error(message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadAdminData();
    return () => {
      cancelled = true;
    };
  }, []);

  const equipmentCountBySlot = useMemo(() => {
    return equipmentItems.reduce((acc, item) => {
      const slot = item.slot || 'misc';
      acc[slot] = (acc[slot] || 0) + 1;
      return acc;
    }, {});
  }, [equipmentItems]);

  const handleEquipmentChange = (field, value) => {
    setEquipmentForm((prev) => ({ ...prev, [field]: value }));
  };

  const startEquipmentEdit = (item) => {
    setEquipmentForm({
      name: item?.name ?? '',
      slot: item?.slot ?? '',
      rarity: item?.rarity ?? 'common',
      cosmetic: Boolean(item?.cosmetic),
      description: item?.description ?? '',
      icon: item?.icon ?? '',
    });
    setEditingEquipmentId(item?.id ?? null);
  };

  const cancelEquipmentEdit = () => {
    setEditingEquipmentId(null);
    setEquipmentForm(createEquipmentForm());
  };

  const handleEquipmentSubmit = async (event) => {
    event.preventDefault();
    const trimmedName = equipmentForm.name.trim();
    if (!trimmedName) {
      toast.error('Назва предмета є обовʼязковою.');
      return;
    }

    const payload = {
      name: trimmedName,
      slot: equipmentForm.slot.trim() || 'misc',
      rarity: equipmentForm.rarity.trim() || 'common',
      cosmetic: Boolean(equipmentForm.cosmetic),
      description: equipmentForm.description.trim() || null,
      icon: equipmentForm.icon.trim() || null,
    };

    try {
      if (editingEquipmentId != null) {
        const updated = await apiPut(`/admin/equipment/${editingEquipmentId}`, payload);
        setEquipmentItems((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
        setEquipmentForm(createEquipmentForm());
        setEditingEquipmentId(null);
        toast.success(`Оновлено предмет: ${updated.name}`);
      } else {
        const created = await apiPost('/admin/equipment', payload);
        setEquipmentItems((prev) => [...prev, created]);
        setEquipmentForm(createEquipmentForm());
        toast.success(`Додано новий предмет: ${created.name}`);
      }
    } catch (error) {
      const message = error?.details || 'Не вдалося зберегти предмет.';
      toast.error(message);
    }
  };

  const handlePlantChange = (field, value) => {
    setPlantForm((prev) => ({ ...prev, [field]: value }));
  };

  const startPlantEdit = (plant) => {
    setPlantForm({
      name: plant?.name ?? '',
      description: plant?.description ?? '',
      growth_seconds: toInputString(plant?.growth_seconds),
      xp_reward: toInputString(plant?.xp_reward),
      energy_cost: toInputString(plant?.energy_cost),
      seed_cost: toInputString(plant?.seed_cost),
      sell_price: toInputString(plant?.sell_price),
      unlock_level: toInputString(plant?.unlock_level),
      unlock_farming_level: toInputString(plant?.unlock_farming_level),
      icon: plant?.icon ?? '',
    });
    setEditingPlantId(plant?.id ?? null);
  };

  const cancelPlantEdit = () => {
    setEditingPlantId(null);
    setPlantForm(createPlantForm());
  };

  const handlePlantSubmit = async (event) => {
    event.preventDefault();
    const trimmedName = plantForm.name.trim();
    if (!trimmedName) {
      toast.error('Назва рослини є обовʼязковою.');
      return;
    }

    const numericFields = [
      ['growth_seconds', 1],
      ['xp_reward', 0],
      ['energy_cost', 0],
      ['seed_cost', 0],
      ['sell_price', 0],
      ['unlock_level', 1],
      ['unlock_farming_level', 1],
    ];

    const plantPayload = {
      name: trimmedName,
      description: plantForm.description.trim() || null,
      icon: plantForm.icon.trim() || null,
    };

    for (const [field, min] of numericFields) {
      const rawValue = plantForm[field];
      const parsed = Number(rawValue);
      if (!Number.isFinite(parsed)) {
        toast.error(`Значення поля "${field}" має бути числом.`);
        return;
      }
      if (parsed < min) {
        toast.error(`Значення поля "${field}" має бути не менше ніж ${min}.`);
        return;
      }
      plantPayload[field] = parsed;
    }

    try {
      if (editingPlantId != null) {
        const updated = await apiPut(`/admin/plants/${editingPlantId}`, plantPayload);
        setPlants((prev) => prev.map((plant) => (plant.id === updated.id ? updated : plant)));
        setPlantForm(createPlantForm());
        setEditingPlantId(null);
        toast.success(`Оновлено рослину: ${updated.name}`);
      } else {
        const created = await apiPost('/admin/plants', plantPayload);
        setPlants((prev) => [...prev, created]);
        setPlantForm(createPlantForm());
        toast.success(`Додано нову рослину: ${created.name}`);
      }
    } catch (error) {
      const message = error?.details || 'Не вдалося зберегти рослину.';
      toast.error(message);
    }
  };

  const handleQuestFieldChange = (field, value) => {
    setQuestForm((prev) => ({ ...prev, [field]: value }));
  };

  const startQuestEdit = (quest) => {
    const nodes = (quest?.nodes ?? []).map((node) => ({
      id: node?.id ?? '',
      title: node?.title ?? '',
      body: node?.body ?? '',
      is_start: Boolean(node?.is_start),
      is_final: Boolean(node?.is_final),
      choices: (node?.choices ?? []).map((choice) => ({
        id: choice?.id ?? '',
        label: choice?.label ?? '',
        next_node_id: choice?.next_node_id ?? '',
        reward_xp: toInputString(choice?.reward_xp, '0'),
        reward_item_id: toInputString(choice?.reward_item_id),
      })),
    }));

    setQuestForm({
      title: quest?.title ?? '',
      description: quest?.description ?? '',
      is_repeatable: Boolean(quest?.is_repeatable),
      nodes: nodes.length > 0 ? nodes : [createEmptyNode({ isStart: true, isFinal: true })],
    });
    setEditingQuestId(quest?.id ?? null);
  };

  const cancelQuestEdit = () => {
    setEditingQuestId(null);
    setQuestForm(createQuestForm());
  };

  const handleQuestNodeChange = (index, field, value) => {
    setQuestForm((prev) => {
      const nodes = prev.nodes.map((node, idx) => {
        if (idx !== index) {
          if (field === 'is_start' && value) {
            return { ...node, is_start: false };
          }
          return node;
        }
        if (field === 'is_start') {
          return { ...node, is_start: value };
        }
        return { ...node, [field]: value };
      });
      return { ...prev, nodes };
    });
  };

  const handleQuestChoiceChange = (nodeIndex, choiceIndex, field, value) => {
    setQuestForm((prev) => {
      const nodes = prev.nodes.map((node, idx) => {
        if (idx !== nodeIndex) {
          return node;
        }
        const choices = node.choices.map((choice, cIdx) => {
          if (cIdx !== choiceIndex) {
            return choice;
          }
          return { ...choice, [field]: value };
        });
        return { ...node, choices };
      });
      return { ...prev, nodes };
    });
  };

  const handleAddQuestNode = () => {
    setQuestForm((prev) => ({
      ...prev,
      nodes: [...prev.nodes, createEmptyNode()],
    }));
  };

  const handleRemoveQuestNode = (index) => {
    setQuestForm((prev) => ({
      ...prev,
      nodes: prev.nodes.filter((_, idx) => idx !== index),
    }));
  };

  const handleAddChoice = (nodeIndex) => {
    setQuestForm((prev) => {
      const nodes = prev.nodes.map((node, idx) => {
        if (idx !== nodeIndex) {
          return node;
        }
        return {
          ...node,
          choices: [...node.choices, createEmptyChoice()],
        };
      });
      return { ...prev, nodes };
    });
  };

  const handleRemoveChoice = (nodeIndex, choiceIndex) => {
    setQuestForm((prev) => {
      const nodes = prev.nodes.map((node, idx) => {
        if (idx !== nodeIndex) {
          return node;
        }
        return {
          ...node,
          choices: node.choices.filter((_, cIdx) => cIdx !== choiceIndex),
        };
      });
      return { ...prev, nodes };
    });
  };

  const handleQuestSubmit = async (event) => {
    event.preventDefault();
    const title = questForm.title.trim();
    if (!title) {
      toast.error('Назва квесту є обовʼязковою.');
      return;
    }

    if (questForm.nodes.length === 0) {
      toast.error('Додайте принаймні один вузол.');
      return;
    }

    const normalizedNodes = [];
    for (const node of questForm.nodes) {
      const trimmedId = node.id.trim();
      if (!trimmedId) {
        toast.error('Кожен вузол має містити ID.');
        return;
      }
      if (!node.title.trim()) {
        toast.error(`Вузол "${trimmedId}" має містити заголовок.`);
        return;
      }
      if (!node.body.trim()) {
        toast.error(`Вузол "${trimmedId}" має містити опис.`);
        return;
      }

      const normalizedChoices = [];
      for (const choice of node.choices) {
        const choiceId = choice.id.trim();
        if (!choiceId) {
          toast.error(`Один із виборів у вузлі "${trimmedId}" не має ID.`);
          return;
        }
        if (!choice.label.trim()) {
          toast.error(`Вибір "${choiceId}" у вузлі "${trimmedId}" має містити текст кнопки.`);
          return;
        }

        const rewardXp = Number(choice.reward_xp);
        if (!Number.isFinite(rewardXp) || rewardXp < 0) {
          toast.error(`Поле "reward_xp" у виборі "${choiceId}" має бути невідʼємним числом.`);
          return;
        }

        const rewardItemId = choice.reward_item_id.trim();
        const normalizedChoice = {
          id: choiceId,
          label: choice.label.trim(),
          next_node_id: choice.next_node_id.trim() || null,
          reward_xp: rewardXp,
          reward_item_id: rewardItemId ? Number(rewardItemId) : null,
        };
        if (rewardItemId && !Number.isInteger(normalizedChoice.reward_item_id)) {
          toast.error(`Поле "reward_item_id" у виборі "${choiceId}" має бути цілим числом.`);
          return;
        }
        normalizedChoices.push(normalizedChoice);
      }

      normalizedNodes.push({
        id: trimmedId,
        title: node.title.trim(),
        body: node.body.trim(),
        is_start: Boolean(node.is_start),
        is_final: Boolean(node.is_final),
        choices: normalizedChoices,
      });
    }

    const payload = {
      title,
      description: questForm.description.trim() || null,
      is_repeatable: Boolean(questForm.is_repeatable),
      nodes: normalizedNodes,
    };

    try {
      if (editingQuestId != null) {
        const updated = await apiPut(`/admin/quests/${editingQuestId}`, payload);
        setQuests((prev) => prev.map((quest) => (quest.id === updated.id ? updated : quest)));
        setQuestForm(createQuestForm());
        setEditingQuestId(null);
        toast.success(`Оновлено квест: ${updated.title}`);
      } else {
        const created = await apiPost('/admin/quests', payload);
        setQuests((prev) => [...prev, created]);
        setQuestForm(createQuestForm());
        toast.success(`Додано новий квест: ${created.title}`);
      }
    } catch (error) {
      const message = error?.details || 'Не вдалося зберегти квест.';
      toast.error(message);
    }
  };

  return (
    <div className="admin-page">
      {loading ? <div className="loader">Завантаження даних адмін-панелі…</div> : null}
      {loadError ? <div className="alert alert--error">{loadError}</div> : null}

      <section className="card admin-section">
        <div className="card__header">
          <h2>Каталог предметів</h2>
          <span className="card__meta">Усього: {equipmentItems.length}</span>
        </div>
        <form className="admin-form" onSubmit={handleEquipmentSubmit}>
          <div className="admin-form__grid">
            <label>
              Назва*
              <input
                type="text"
                className="admin-input"
                value={equipmentForm.name}
                onChange={(event) => handleEquipmentChange('name', event.target.value)}
                placeholder="Напр. Меч героя"
              />
            </label>
            <label>
              Слот
              <input
                type="text"
                className="admin-input"
                value={equipmentForm.slot}
                onChange={(event) => handleEquipmentChange('slot', event.target.value)}
                placeholder="weapon / head / misc"
              />
            </label>
            <label>
              Рідкісність
              <select
                className="admin-select"
                value={equipmentForm.rarity}
                onChange={(event) => handleEquipmentChange('rarity', event.target.value)}
              >
                {rarityOptions.map((rarity) => (
                  <option key={rarity} value={rarity}>
                    {rarity}
                  </option>
                ))}
              </select>
            </label>
            <label className="admin-checkbox-row">
              <input
                type="checkbox"
                checked={equipmentForm.cosmetic}
                onChange={(event) => handleEquipmentChange('cosmetic', event.target.checked)}
              />
              Козметичний предмет
            </label>
          </div>
          <div className="admin-form__grid">
            <label>
              Опис
              <textarea
                className="admin-textarea"
                value={equipmentForm.description}
                onChange={(event) => handleEquipmentChange('description', event.target.value)}
                rows={3}
              />
            </label>
            <label>
              Іконка
              <input
                type="text"
                className="admin-input"
                value={equipmentForm.icon}
                onChange={(event) => handleEquipmentChange('icon', event.target.value)}
                placeholder="Напр. item_sword_hero"
              />
            </label>
          </div>
          <div className="admin-form__actions">
            <button type="submit" className="btn btn--primary">
              {editingEquipmentId != null ? 'Оновити предмет' : 'Додати предмет'}
            </button>
            {editingEquipmentId != null ? (
              <button type="button" className="btn btn--secondary btn--compact" onClick={cancelEquipmentEdit}>
                Скасувати
              </button>
            ) : null}
          </div>
          {editingEquipmentId != null ? (
            <div className="admin-hint">Редагуємо предмет #{editingEquipmentId}. Після збереження зміни одразу застосуються.</div>
          ) : null}
        </form>
        <div className="admin-table-wrapper">
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Назва</th>
                <th>Слот</th>
                <th>Рідкісність</th>
                <th>Козм.</th>
                <th>Іконка</th>
                <th>Дії</th>
              </tr>
            </thead>
            <tbody>
              {equipmentItems.map((item) => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>{item.name}</td>
                  <td>
                    {item.slot || 'misc'}
                    {equipmentCountBySlot[item.slot || 'misc'] > 1 ? (
                      <span className="admin-table__badge">{equipmentCountBySlot[item.slot || 'misc']}</span>
                    ) : null}
                  </td>
                  <td>{item.rarity}</td>
                  <td>{item.cosmetic ? 'Так' : 'Ні'}</td>
                  <td>{item.icon || '—'}</td>
                  <td>
                    <button
                      type="button"
                      className="btn btn--secondary btn--compact"
                      onClick={() => startEquipmentEdit(item)}
                    >
                      Редагувати
                    </button>
                  </td>
                </tr>
              ))}
              {equipmentItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="admin-table__empty">
                    Каталог порожній. Додайте перший предмет.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card admin-section">
        <div className="card__header">
          <h2>Каталог рослин</h2>
          <span className="card__meta">Усього: {plants.length}</span>
        </div>
        <form className="admin-form" onSubmit={handlePlantSubmit}>
          <div className="admin-form__grid">
            <label>
              Назва*
              <input
                type="text"
                className="admin-input"
                value={plantForm.name}
                onChange={(event) => handlePlantChange('name', event.target.value)}
                placeholder="Напр. Срібна троянда"
              />
            </label>
            <label>
              Час росту (сек)*
              <input
                type="number"
                min="1"
                className="admin-input"
                value={plantForm.growth_seconds}
                onChange={(event) => handlePlantChange('growth_seconds', event.target.value)}
              />
            </label>
            <label>
              XP за збір*
              <input
                type="number"
                min="0"
                className="admin-input"
                value={plantForm.xp_reward}
                onChange={(event) => handlePlantChange('xp_reward', event.target.value)}
              />
            </label>
            <label>
              Вартість енергії*
              <input
                type="number"
                min="0"
                className="admin-input"
                value={plantForm.energy_cost}
                onChange={(event) => handlePlantChange('energy_cost', event.target.value)}
              />
            </label>
            <label>
              Вартість насіння*
              <input
                type="number"
                min="0"
                className="admin-input"
                value={plantForm.seed_cost}
                onChange={(event) => handlePlantChange('seed_cost', event.target.value)}
              />
            </label>
            <label>
              Ціна продажу*
              <input
                type="number"
                min="0"
                className="admin-input"
                value={plantForm.sell_price}
                onChange={(event) => handlePlantChange('sell_price', event.target.value)}
              />
            </label>
            <label>
              Рівень гравця*
              <input
                type="number"
                min="1"
                className="admin-input"
                value={plantForm.unlock_level}
                onChange={(event) => handlePlantChange('unlock_level', event.target.value)}
              />
            </label>
            <label>
              Рівень фермерства*
              <input
                type="number"
                min="1"
                className="admin-input"
                value={plantForm.unlock_farming_level}
                onChange={(event) => handlePlantChange('unlock_farming_level', event.target.value)}
              />
            </label>
          </div>
          <div className="admin-form__grid">
            <label>
              Опис
              <textarea
                className="admin-textarea"
                value={plantForm.description}
                onChange={(event) => handlePlantChange('description', event.target.value)}
                rows={3}
              />
            </label>
            <label>
              Іконка
              <input
                type="text"
                className="admin-input"
                value={plantForm.icon}
                onChange={(event) => handlePlantChange('icon', event.target.value)}
                placeholder="Напр. plant_crystal_flower"
              />
            </label>
          </div>
          <div className="admin-form__actions">
            <button type="submit" className="btn btn--primary">
              {editingPlantId != null ? 'Оновити рослину' : 'Додати рослину'}
            </button>
            {editingPlantId != null ? (
              <button type="button" className="btn btn--secondary btn--compact" onClick={cancelPlantEdit}>
                Скасувати
              </button>
            ) : null}
          </div>
          {editingPlantId != null ? (
            <div className="admin-hint">Редагуємо рослину #{editingPlantId}. Нові значення замінять попередні.</div>
          ) : null}
        </form>

        <div className="admin-table-wrapper">
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Назва</th>
                <th>XP</th>
                <th>Енергія</th>
                <th>Насіння</th>
                <th>Продаж</th>
                <th>Рівні</th>
                <th>Дії</th>
              </tr>
            </thead>
            <tbody>
              {plants.map((plant) => (
                <tr key={plant.id}>
                  <td>{plant.id}</td>
                  <td>{plant.name}</td>
                  <td>{plant.xp_reward}</td>
                  <td>{plant.energy_cost}</td>
                  <td>{plant.seed_cost}</td>
                  <td>{plant.sell_price}</td>
                  <td>
                    {plant.unlock_level}/{plant.unlock_farming_level}
                  </td>
                  <td>
                    <button
                      type="button"
                      className="btn btn--secondary btn--compact"
                      onClick={() => startPlantEdit(plant)}
                    >
                      Редагувати
                    </button>
                  </td>
                </tr>
              ))}
              {plants.length === 0 ? (
                <tr>
                  <td colSpan={8} className="admin-table__empty">
                    Каталог рослин порожній.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card admin-section">
        <div className="card__header">
          <h2>Квести</h2>
          <span className="card__meta">Усього: {quests.length}</span>
        </div>
        <form className="admin-form" onSubmit={handleQuestSubmit}>
          <div className="admin-form__grid">
            <label>
              Назва*
              <input
                type="text"
                className="admin-input"
                value={questForm.title}
                onChange={(event) => handleQuestFieldChange('title', event.target.value)}
                placeholder="Напр. Порятунок ферми"
              />
            </label>
            <label className="admin-checkbox-row">
              <input
                type="checkbox"
                checked={questForm.is_repeatable}
                onChange={(event) => handleQuestFieldChange('is_repeatable', event.target.checked)}
              />
              Повторюваний квест
            </label>
          </div>
          <label>
            Опис
            <textarea
              className="admin-textarea"
              value={questForm.description}
              onChange={(event) => handleQuestFieldChange('description', event.target.value)}
              rows={3}
            />
          </label>

          <div className="admin-quest-nodes">
            {questForm.nodes.map((node, index) => (
              <fieldset key={index} className="admin-quest-node">
                <legend>Вузол #{index + 1}</legend>
                <div className="admin-form__grid">
                  <label>
                    ID вузла*
                    <input
                      type="text"
                      className="admin-input"
                      value={node.id}
                      onChange={(event) => handleQuestNodeChange(index, 'id', event.target.value)}
                      placeholder="Напр. intro"
                    />
                  </label>
                  <label>
                    Заголовок*
                    <input
                      type="text"
                      className="admin-input"
                      value={node.title}
                      onChange={(event) => handleQuestNodeChange(index, 'title', event.target.value)}
                      placeholder="Напр. Складні часи"
                    />
                  </label>
                </div>
                <label>
                  Опис*
                  <textarea
                    className="admin-textarea"
                    value={node.body}
                    onChange={(event) => handleQuestNodeChange(index, 'body', event.target.value)}
                    rows={3}
                  />
                </label>
                <div className="admin-checkbox-group">
                  <label className="admin-checkbox-row">
                    <input
                      type="checkbox"
                      checked={node.is_start}
                      onChange={(event) => handleQuestNodeChange(index, 'is_start', event.target.checked)}
                    />
                    Стартовий вузол
                  </label>
                  <label className="admin-checkbox-row">
                    <input
                      type="checkbox"
                      checked={node.is_final}
                      onChange={(event) => handleQuestNodeChange(index, 'is_final', event.target.checked)}
                    />
                    Фінальний вузол
                  </label>
                  <button
                    type="button"
                    className="btn btn--secondary btn--compact"
                    onClick={() => handleRemoveQuestNode(index)}
                    disabled={questForm.nodes.length <= 1}
                  >
                    Видалити вузол
                  </button>
                </div>

                <div className="admin-choices">
                  <div className="admin-choices__header">
                    <h4>Варіанти переходів</h4>
                    <button
                      type="button"
                      className="btn btn--secondary btn--compact"
                      onClick={() => handleAddChoice(index)}
                    >
                      Додати вибір
                    </button>
                  </div>
                  {node.choices.length === 0 ? (
                    <div className="admin-choice admin-choice--empty">
                      Ще немає варіантів. Додайте перший.
                    </div>
                  ) : (
                    node.choices.map((choice, choiceIndex) => (
                      <div key={choiceIndex} className="admin-choice">
                        <div className="admin-choice__row">
                          <label>
                            ID вибору*
                            <input
                              type="text"
                              className="admin-input"
                              value={choice.id}
                              onChange={(event) =>
                                handleQuestChoiceChange(index, choiceIndex, 'id', event.target.value)
                              }
                              placeholder="Напр. help"
                            />
                          </label>
                          <label>
                            Текст кнопки*
                            <input
                              type="text"
                              className="admin-input"
                              value={choice.label}
                              onChange={(event) =>
                                handleQuestChoiceChange(index, choiceIndex, 'label', event.target.value)
                              }
                              placeholder="Напр. Допомогти фермеру"
                            />
                          </label>
                        </div>
                        <div className="admin-choice__row">
                          <label>
                            Наступний вузол
                            <input
                              type="text"
                              className="admin-input"
                              value={choice.next_node_id}
                              onChange={(event) =>
                                handleQuestChoiceChange(index, choiceIndex, 'next_node_id', event.target.value)
                              }
                              placeholder="ID вузла або порожньо"
                            />
                          </label>
                          <label>
                            XP
                            <input
                              type="number"
                              min="0"
                              className="admin-input"
                              value={choice.reward_xp}
                              onChange={(event) =>
                                handleQuestChoiceChange(index, choiceIndex, 'reward_xp', event.target.value)
                              }
                            />
                          </label>
                          <label>
                            ID предмета
                            <input
                              type="number"
                              min="1"
                              className="admin-input"
                              value={choice.reward_item_id}
                              onChange={(event) =>
                                handleQuestChoiceChange(index, choiceIndex, 'reward_item_id', event.target.value)
                              }
                              placeholder="Опціонально"
                            />
                          </label>
                        </div>
                        <div className="admin-choice__actions">
                          <button
                            type="button"
                            className="btn btn--secondary btn--compact"
                            onClick={() => handleRemoveChoice(index, choiceIndex)}
                          >
                            Видалити вибір
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </fieldset>
            ))}
            <button type="button" className="btn btn--secondary" onClick={handleAddQuestNode}>
              Додати вузол
            </button>
          </div>
          <div className="admin-form__actions">
            <button type="submit" className="btn btn--primary">
              {editingQuestId != null ? 'Оновити квест' : 'Зберегти квест'}
            </button>
            {editingQuestId != null ? (
              <button type="button" className="btn btn--secondary btn--compact" onClick={cancelQuestEdit}>
                Скасувати
              </button>
            ) : null}
          </div>
          {editingQuestId != null ? (
            <div className="admin-hint">
              Редагуємо квест #{editingQuestId}. Усі вузли та переходи будуть оновлені відповідно до нових даних.
            </div>
          ) : null}
        </form>

        <div className="admin-quest-list">
          {quests.length === 0 ? (
            <div className="admin-table__empty">Ще немає квестів.</div>
          ) : (
            quests.map((quest) => (
              <details key={quest.id} className="admin-quest">
                <summary>
                  <div className="admin-quest__summary">
                    <div className="admin-quest__summary-info">
                      <strong>{quest.title}</strong>
                      {quest.is_repeatable ? <span className="admin-badge">repeatable</span> : null}
                      {editingQuestId === quest.id ? (
                        <span className="admin-badge admin-badge--highlight">редагується</span>
                      ) : null}
                    </div>
                    <button
                      type="button"
                      className="btn btn--secondary btn--compact"
                      onClick={(event) => {
                        event.preventDefault();
                        event.stopPropagation();
                        startQuestEdit(quest);
                      }}
                    >
                      Редагувати
                    </button>
                  </div>
                </summary>
                <p>{quest.description || '—'}</p>
                <ul>
                  {quest.nodes.map((node) => (
                    <li key={node.id} className="admin-quest__node">
                      <div className="admin-quest__node-title">
                        <strong>{node.id}</strong> — {node.title}{' '}
                        {node.is_start ? <span className="admin-badge admin-badge--highlight">start</span> : null}
                        {node.is_final ? <span className="admin-badge">final</span> : null}
                      </div>
                      <p>{node.body}</p>
                      {node.choices.length > 0 ? (
                        <table className="admin-table admin-table--dense">
                          <thead>
                            <tr>
                              <th>ID</th>
                              <th>Текст</th>
                              <th>Next</th>
                              <th>XP</th>
                              <th>Item</th>
                            </tr>
                          </thead>
                          <tbody>
                            {node.choices.map((choice) => (
                              <tr key={choice.id}>
                                <td>{choice.id}</td>
                                <td>{choice.label}</td>
                                <td>{choice.next_node_id || '—'}</td>
                                <td>{choice.reward_xp}</td>
                                <td>{choice.reward_item_id || '—'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      ) : (
                        <div className="admin-table__empty">Немає варіантів переходу.</div>
                      )}
                    </li>
                  ))}
                </ul>
              </details>
            ))
          )}
        </div>
      </section>
    </div>
  );
}

export default AdminPage;
