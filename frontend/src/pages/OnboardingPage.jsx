import { useMemo } from 'react';
import toast from 'react-hot-toast';
import { usePlayerStore } from '../store/usePlayerStore.js';
import { useOnboardingStore } from '../store/useOnboardingStore.js';

function OnboardingStep({ step, index }) {
  return (
    <li className="onboarding__step">
      <div className="onboarding__step-index">{String(index + 1).padStart(2, '0')}</div>
      <div>
        <h3>{step.title}</h3>
        <p>{step.body}</p>
      </div>
    </li>
  );
}

function QuestPreview({ node }) {
  if (!node) {
    return null;
  }

  return (
    <section className="onboarding__card">
      <header>
        <h2>{node.title}</h2>
        <span className="onboarding__tag">Початковий квест</span>
      </header>
      <p>{node.body}</p>
      {Array.isArray(node.choices) && node.choices.length ? (
        <ul className="onboarding__choices">
          {node.choices.map((choice) => (
            <li key={choice.choice_id}>
              <strong>{choice.label}</strong>
              <span>Нагорода: +{choice.reward_xp ?? 0} XP</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="onboarding__hint">Закінчи привітання, щоб перейти до квесту.</p>
      )}
    </section>
  );
}

function OnboardingPage() {
  const playerId = usePlayerStore((state) => state.playerId);
  const fetchDashboard = usePlayerStore((state) => state.fetchDashboard);
  const { data, loading, complete } = useOnboardingStore();
  const error = useOnboardingStore((state) => state.error);

  const steps = data?.steps ?? [];
  const starterSeeds = data?.starter_seed_charges ?? 0;

  const handleComplete = async () => {
    if (!Number.isFinite(playerId)) return;
    try {
      const result = await complete(playerId);
      if (result?.completed) {
        toast.success('Вперед до ферми!');
        await fetchDashboard();
      }
    } catch (error) {
      toast.error(error?.message ?? 'Сталася помилка. Спробуй ще раз.');
    }
  };

  const disabled = useMemo(() => loading || !Number.isFinite(playerId), [loading, playerId]);

  return (
    <div className="onboarding">
      <section className="onboarding__hero">
        <p className="onboarding__eyebrow">Нова пригода</p>
        <h1>Ласкаво просимо до власної ферми</h1>
        <p>
          Отримай подарункове насіння (залишилось {starterSeeds}) та пройди коротке знайомство, щоб
          вирушити у перший квест.
        </p>
      </section>

      <section className="onboarding__card">
        <header>
          <h2>Коротко про головне</h2>
          <span className="onboarding__tag onboarding__tag--accent">3 кроки</span>
        </header>
        <ol className="onboarding__steps">
          {steps.map((step, index) => (
            <OnboardingStep key={step.title} step={step} index={index} />
          ))}
        </ol>
      </section>

      {error ? <p className="onboarding__error">{error}</p> : null}

      <QuestPreview node={data?.current_node} />

      <div className="onboarding__actions">
        <button type="button" className="btn btn--primary" onClick={handleComplete} disabled={disabled}>
          {loading ? 'Зачекайте…' : 'Почати пригоди'}
        </button>
      </div>
    </div>
  );
}

export default OnboardingPage;
