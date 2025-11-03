import { useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import { useAuthStore } from '../store/useAuthStore.js';

function ModeToggle({ mode, onChange }) {
  return (
    <div className="start-page__mode">
      <button
        type="button"
        className={`btn ${mode === 'register' ? 'btn--primary' : 'btn--ghost'}`}
        onClick={() => onChange('register')}
      >
        Створити героя
      </button>
      <button
        type="button"
        className={`btn ${mode === 'login' ? 'btn--primary' : 'btn--ghost'}`}
        onClick={() => onChange('login')}
      >
        У мене вже є герой
      </button>
    </div>
  );
}

function StartPage() {
  const [mode, setMode] = useState('register');
  const [form, setForm] = useState({ login: '', password: '', heroName: '' });

  const register = useAuthStore((state) => state.register);
  const login = useAuthStore((state) => state.login);
  const loading = useAuthStore((state) => state.loading);
  const error = useAuthStore((state) => state.error);
  const clearError = useAuthStore((state) => state.clearError);

  const title = useMemo(
    () =>
      mode === 'register'
        ? 'Створи власного героя'
        : 'Увійди, щоб продовжити пригоду',
    [mode],
  );

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleModeChange = (nextMode) => {
    if (nextMode === mode) {
      return;
    }
    setMode(nextMode);
    clearError();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      if (mode === 'register') {
        await register({
          login: form.login,
          password: form.password,
          hero_name: form.heroName,
        });
        toast.success('Героя створено! Починай знайомство з фермою.');
      } else {
        await login({
          login: form.login,
          password: form.password,
        });
        toast.success('Вітаємо з поверненням!');
      }
    } catch (submitError) {
      const message = submitError?.details || submitError?.message || 'Сталася помилка.';
      toast.error(message);
    }
  };

  return (
    <div className="start-page">
      <section className="start-page__intro">
        <h1>Ultimate App</h1>
        <p>
          Рости героя, доглядай ферму та вирушай у перші квести. Почни з короткого знайомства,
          щоб відкрити перший квест «Знайомство».
        </p>
      </section>

      <ModeToggle mode={mode} onChange={handleModeChange} />

      <form className="start-page__form" onSubmit={handleSubmit}>
        <h2>{title}</h2>

        <label className="start-page__field">
          <span>Логін</span>
          <input
            type="text"
            name="login"
            autoComplete="username"
            value={form.login}
            onChange={handleChange}
            required
          />
        </label>

        <label className="start-page__field">
          <span>Пароль</span>
          <input
            type="password"
            name="password"
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            value={form.password}
            onChange={handleChange}
            required
            minLength={6}
          />
        </label>

        {mode === 'register' ? (
          <label className="start-page__field">
            <span>Ім&apos;я героя</span>
            <input
              type="text"
              name="heroName"
              value={form.heroName}
              onChange={handleChange}
              required
              minLength={1}
            />
          </label>
        ) : null}

        {error ? <p className="start-page__error">{error}</p> : null}

        <button type="submit" className="btn btn--primary btn--full" disabled={loading}>
          {loading ? 'Зачекайте…' : mode === 'register' ? 'Створити героя' : 'Увійти'}
        </button>
      </form>
    </div>
  );
}

export default StartPage;
