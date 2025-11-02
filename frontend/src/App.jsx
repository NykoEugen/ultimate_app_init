import { useEffect, useState } from 'react';
import { Route, Routes } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import TopNav from './components/TopNav';
import DashboardPage from './pages/DashboardPage.jsx';
import InventoryPage from './pages/InventoryPage.jsx';
import ShopPage from './pages/ShopPage.jsx';
import FarmPage from './pages/FarmPage.jsx';
import { usePlayerStore } from './store/usePlayerStore.js';
import { useOnboardingStore } from './store/useOnboardingStore.js';
import OnboardingPage from './pages/OnboardingPage.jsx';

function PageContainer({ title, children }) {
  return (
    <section className="page">
      <h1>{title}</h1>
      <div className="page__body">{children}</div>
    </section>
  );
}

function App() {
  const [theme, setTheme] = useState(() => {
    if (typeof window === 'undefined') {
      return 'light';
    }
    const stored = window.localStorage.getItem('ultimate-app-theme');
    if (stored === 'light' || stored === 'dark') {
      return stored;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  const playerId = usePlayerStore((state) => state.playerId);
  const fetchDashboard = usePlayerStore((state) => state.fetchDashboard);

  const onboardingData = useOnboardingStore((state) => state.data);
  const onboardingLoading = useOnboardingStore((state) => state.loading);
  const onboardingError = useOnboardingStore((state) => state.error);
  const fetchOnboarding = useOnboardingStore((state) => state.fetch);
  const resetOnboarding = useOnboardingStore((state) => state.reset);

  useEffect(() => {
    if (Number.isFinite(playerId)) {
      fetchDashboard();
      fetchOnboarding(playerId);
    }
  }, [playerId, fetchDashboard, fetchOnboarding]);

  useEffect(() => {
    if (!Number.isFinite(playerId)) {
      resetOnboarding();
    }
  }, [playerId, resetOnboarding]);

  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    root.dataset.theme = theme;
    window.localStorage.setItem('ultimate-app-theme', theme);
  }, [theme]);

  useEffect(() => {
    const listener = (event) => {
      setTheme(event.matches ? 'dark' : 'light');
    };

    if (typeof window !== 'undefined') {
      const media = window.matchMedia('(prefers-color-scheme: dark)');
      media.addEventListener('change', listener);
      return () => media.removeEventListener('change', listener);
    }

    return undefined;
  }, []);

  const toggleTheme = () => {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className="app-shell">
      <TopNav theme={theme} onToggleTheme={toggleTheme} />
      <main className="app-content">
        {Number.isFinite(playerId) && onboardingData && !onboardingData.completed ? (
          <OnboardingPage />
        ) : Number.isFinite(playerId) && onboardingLoading && !onboardingData ? (
          <div className="onboarding-loading">Завантаження привітання…</div>
        ) : Number.isFinite(playerId) && onboardingError && !onboardingData ? (
          <div className="onboarding-loading onboarding-loading--error">{onboardingError}</div>
        ) : (
          <Routes>
            <Route
              path="/"
              element={
                <PageContainer title="Dashboard">
                  <DashboardPage />
                </PageContainer>
              }
            />
            <Route
              path="/inventory"
              element={
                <PageContainer title="Inventory">
                  <InventoryPage />
                </PageContainer>
              }
            />
            <Route
              path="/shop"
              element={
                <PageContainer title="Shop">
                  <ShopPage />
                </PageContainer>
              }
            />
            <Route
              path="/farm"
              element={
                <PageContainer title="My Farm">
                  <FarmPage />
                </PageContainer>
              }
            />
          </Routes>
        )}
      </main>
      <Toaster position="top-right" />
    </div>
  );
}

export default App;
