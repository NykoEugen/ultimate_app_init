import { useEffect, useState } from 'react';
import { Route, Routes } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import TopNav from './components/TopNav';
import DashboardPage from './pages/DashboardPage.jsx';
import InventoryPage from './pages/InventoryPage.jsx';
import ShopPage from './pages/ShopPage.jsx';
import FarmPage from './pages/FarmPage.jsx';
import AdminPage from './pages/AdminPage.jsx';
import StartPage from './pages/StartPage.jsx';
import OnboardingPage from './pages/OnboardingPage.jsx';
import { usePlayerStore } from './store/usePlayerStore.js';
import { useOnboardingStore } from './store/useOnboardingStore.js';
import { useAuthStore } from './store/useAuthStore.js';

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
  const playerProfile = usePlayerStore((state) => state.profile);

  const onboardingData = useOnboardingStore((state) => state.data);
  const onboardingLoading = useOnboardingStore((state) => state.loading);
  const onboardingError = useOnboardingStore((state) => state.error);
  const fetchOnboarding = useOnboardingStore((state) => state.fetch);
  const resetOnboarding = useOnboardingStore((state) => state.reset);

  const hydrateAuth = useAuthStore((state) => state.hydrate);
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  useEffect(() => {
    hydrateAuth();
  }, [hydrateAuth]);

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

  const isAuthenticated = Boolean(token && user);
  const isAdmin = Boolean(user?.is_admin);

  if (!isAuthenticated) {
    return (
      <div className="app-shell app-shell--start">
        <main className="app-content">
          <StartPage />
        </main>
        <Toaster position="top-right" />
      </div>
    );
  }

  return (
    <div className="app-shell">
      <TopNav theme={theme} onToggleTheme={toggleTheme} player={playerProfile} user={user} onLogout={logout} />
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
            <Route
              path="/admin"
              element={
                <PageContainer title="Admin Panel">
                  {isAdmin ? <AdminPage /> : <p>Доступ дозволено лише адміністраторам.</p>}
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
