export function formatSecondsToHMS(seconds) {
  const totalSeconds = Number.isFinite(seconds) ? seconds : Number(seconds);
  const safeSeconds = Number.isFinite(totalSeconds) && totalSeconds > 0 ? Math.floor(totalSeconds) : 0;

  const hours = Math.floor(safeSeconds / 3600);
  const minutes = Math.floor((safeSeconds % 3600) / 60);
  const secs = safeSeconds % 60;

  const parts = [
    hours > 0 ? String(hours) : null,
    hours > 0 ? String(minutes).padStart(2, '0') : String(minutes),
    String(secs).padStart(2, '0'),
  ].filter((part) => part !== null);

  const [first, ...rest] = parts;
  return [first, ...rest.map((value) => value.padStart(2, '0'))].join(':');
}

const rarityMap = {
  common: 'badge badge--common',
  uncommon: 'badge badge--uncommon',
  rare: 'badge badge--rare',
  epic: 'badge badge--epic',
  legendary: 'badge badge--legendary',
};

export function rarityClass(rarity) {
  if (!rarity) {
    return 'badge';
  }

  const key = String(rarity).trim().toLowerCase();
  return rarityMap[key] ?? `badge badge--${key.replace(/\s+/g, '-')}`;
}
