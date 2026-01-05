type View =
  | 'welcome'
  | 'login'
  | 'signup'
  | 'studio'
  | 'game'
  | 'leaderboard'
  | 'playerLogin'
  | 'playerSim'
  | 'settings';

type FilterKind = 'all' | '1h' | '6h' | '24h' | '48h' | 'custom';

type SortKey = 'xid' | 'score' | 'updatedOn';

interface FilterState {
  kind: FilterKind;
  start?: string;
  end?: string;
}

interface ScoreEntry {
  xid: string;
  score: number;
  updatedOn: string;
}

interface LeaderboardSummary {
  leaderboard_id: string;
  name?: string;
  sort_order: 'asc' | 'desc';
}

interface GameSummary {
  game_id: string;
  name: string;
  leaderboards: LeaderboardSummary[];
}

interface Studio {
  company_id: string;
  name: string;
  games: GameSummary[];
}

interface LeaderboardData {
  leaderboardId: string;
  entries: ScoreEntry[];
  total: number;
  sortOrder: 'asc' | 'desc';
}

interface LeaderboardOption {
  leaderboard_id: string;
  name?: string;
  sort_order: 'asc' | 'desc';
}

interface Session {
  companyId: string;
  companySecret: string;
  expiresAt: number;
}

interface PlayerSession {
  deviceId: string;
  xid?: string;
}

interface AppState {
  view: View;
  studio?: Studio;
  selectedGameId?: string;
  selectedLeaderboardId?: string;
  sortKey: SortKey;
  sortDir: 'asc' | 'desc';
  filter: FilterState;
  filterOpen: boolean;
  page: number;
  authMessage?: string;
  session?: Session;
  loading: boolean;
  leaderboardData?: LeaderboardData;
  playerSession?: PlayerSession;
  playerMessage?: string;
  expandedGames?: Record<string, boolean>;
}

const app = document.querySelector<HTMLDivElement>('#app')!;

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';
const SESSION_KEY = 'lx-session';
const UI_STATE_KEY = 'lx-ui-state';
const SESSION_TTL_MS = 7 * 24 * 60 * 60 * 1000; // configurable: one week
const ROUTE_PREFIX = '/';

const state: AppState = {
  view: 'welcome',
  sortKey: 'score',
  sortDir: 'desc',
  filter: { kind: '24h' },
  filterOpen: false,
  page: 1,
  loading: false,
  expandedGames: {}
};

function renderApp(): void {
  switch (state.view) {
    case 'welcome':
      renderWelcome();
      break;
    case 'login':
      renderAuth('login');
      break;
    case 'signup':
      renderAuth('signup');
      break;
    case 'studio':
      renderStudioDashboard();
      break;
    case 'game':
      renderGameDashboard();
      break;
    case 'leaderboard':
      renderLeaderboardDashboard();
      break;
    case 'playerLogin':
      renderPlayerLoginPage();
    break;
    case 'playerSim':
      renderPlayerSimulatorPage();
      break;
    case 'settings':
      renderSettings();
      break;
  }
}

function saveSession(session: Session): void {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

function clearSession(): void {
  localStorage.removeItem(SESSION_KEY);
}

function handleLogout(): void {
  state.session = undefined;
  state.studio = undefined;
  state.selectedGameId = undefined;
  state.selectedLeaderboardId = undefined;
  state.leaderboardData = undefined;
  state.playerSession = undefined;
  state.playerMessage = undefined;
  clearSession();
  localStorage.removeItem(UI_STATE_KEY);
  navigate('welcome', { push: true });
}

function loadSession(): Session | undefined {
  const raw = localStorage.getItem(SESSION_KEY);
  if (!raw) return undefined;
  try {
    const session = JSON.parse(raw) as Session;
    if (session.expiresAt && session.expiresAt > Date.now()) {
      return session;
    }
  } catch (e) {
    console.error('Failed to parse session', e);
  }
  clearSession();
  return undefined;
}

function saveUiState(): void {
  const payload = {
    selectedGameId: state.selectedGameId,
    selectedLeaderboardId: state.selectedLeaderboardId,
    view: state.view
  };
  localStorage.setItem(UI_STATE_KEY, JSON.stringify(payload));
  syncUrl();
}

function loadUiState(): { selectedGameId?: string; selectedLeaderboardId?: string; view?: View } {
  const raw = localStorage.getItem(UI_STATE_KEY);
  if (!raw) return {};
  try {
    return JSON.parse(raw) as { selectedGameId?: string; selectedLeaderboardId?: string; view?: View };
  } catch (e) {
    console.error('Failed to parse UI state', e);
    return {};
  }
}

function syncUrl(): void {
  const url = new URL(window.location.href);
  url.searchParams.set('view', state.view);
  if (state.selectedGameId) {
    url.searchParams.set('game', state.selectedGameId);
  } else {
    url.searchParams.delete('game');
  }
  if (state.selectedLeaderboardId) {
    url.searchParams.set('leaderboard', state.selectedLeaderboardId);
  } else {
    url.searchParams.delete('leaderboard');
  }
  window.history.replaceState({}, '', url.toString());
}

function readUrlState(): { view?: View; selectedGameId?: string; selectedLeaderboardId?: string } {
  const url = new URL(window.location.href);
  const view = url.searchParams.get('view') as View | null;
  const selectedGameId = url.searchParams.get('game') || undefined;
  const selectedLeaderboardId = url.searchParams.get('leaderboard') || undefined;
  return { view: view || undefined, selectedGameId, selectedLeaderboardId };
}

function navigate(view: View, opts?: { gameId?: string; leaderboardId?: string; push?: boolean }): void {
  state.view = view;
  if (opts?.gameId !== undefined) state.selectedGameId = opts.gameId;
  if (opts?.leaderboardId !== undefined) state.selectedLeaderboardId = opts.leaderboardId;
  const url = new URL(window.location.href);
  url.searchParams.set('view', view);
  if (state.selectedGameId) url.searchParams.set('game', state.selectedGameId);
  else url.searchParams.delete('game');
  if (state.selectedLeaderboardId) url.searchParams.set('leaderboard', state.selectedLeaderboardId);
  else url.searchParams.delete('leaderboard');
  if (opts?.push) {
    window.history.pushState({}, '', url.toString());
  } else {
    window.history.replaceState({}, '', url.toString());
  }
  renderApp();
}

function buildSidebarTree(): string {
  if (!state.studio) return '';
  const games = state.studio.games || [];
  return games
    .map((g) => {
      const expanded = state.expandedGames?.[g.game_id] ?? g.game_id === state.selectedGameId;
      const leaderboards = expanded
        ? `<div class="tree-children">
            ${g.leaderboards
              .map(
                (lb) =>
                  `<div class="tree-leaf" data-type="leaderboard" data-game="${g.game_id}" data-lb="${lb.leaderboard_id}">
                    ${lb.name || lb.leaderboard_id}
                  </div>`
              )
              .join('')}
          </div>`
        : '';
      return `
        <div class="tree-node">
          <div class="tree-row ${expanded ? 'open' : ''}" data-type="game" data-game="${g.game_id}">
            <span class="caret">${expanded ? '▾' : '▸'}</span>
            <span>${g.name}</span>
          </div>
          ${leaderboards}
        </div>
      `;
    })
    .join('');
}

async function fetchCompanySummary(companyId: string, companySecret: string): Promise<Studio> {
  const url = new URL(`${API_BASE}/studio/company`);
  url.searchParams.set('company_id', companyId);
  url.searchParams.set('company_secret', companySecret);
  const res = await fetch(url.toString());
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || 'Unable to fetch company summary');
  }
  const data = await res.json();
  return data as Studio;
}

async function registerCompany(name: string): Promise<{ company_id: string; company_secret: string; name: string }> {
  const res = await fetch(`${API_BASE}/studio/companies`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || 'Unable to register company');
  }
  return res.json();
}

async function fetchLeaderboardEntries(
  gameId: string,
  leaderboardId: string,
  page: number,
  pageSize: number
): Promise<LeaderboardData> {
  const url = new URL(`${API_BASE}/client/leaderboard`);
  url.searchParams.set('game_id', gameId);
  url.searchParams.set('leaderboard_id', leaderboardId);
  url.searchParams.set('limit', pageSize.toString());
  url.searchParams.set('offset', ((page - 1) * pageSize).toString());
  const res = await fetch(url.toString());
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || 'Unable to fetch leaderboard');
  }
  const data = await res.json();
  return {
    leaderboardId,
    entries: (data.entries || []).map((e: any) => ({
      xid: e.xid,
      score: e.best_value,
      updatedOn: e.updated_at
    })),
    total: data.total,
    sortOrder: data.sort_order
  };
}

async function clientAuth(gameId: string, deviceId: string): Promise<{ xid: string; is_new: boolean }> {
  const res = await fetch(`${API_BASE}/client/auth`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ game_id: gameId, device_id: deviceId })
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || 'Unable to auth device');
  }
  return res.json();
}

async function clientSubmitScore(gameId: string, leaderboardId: string, xid: string, value: number): Promise<void> {
  const res = await fetch(`${API_BASE}/client/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ game_id: gameId, leaderboard_id: leaderboardId, xid, value })
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || 'Unable to submit score');
  }
}

async function loadPreviewLeaderboard(gameId: string, leaderboardId: string): Promise<void> {
  try {
    state.loading = true;
    const data = await fetchLeaderboardEntries(gameId, leaderboardId, 1, 50);
    if (state.selectedLeaderboardId === leaderboardId) {
      state.leaderboardData = data;
    }
  } catch (e) {
    state.playerMessage = (e as Error).message;
  } finally {
    state.loading = false;
  }
}
async function openLeaderboard(gameId: string, leaderboardId: string, page: number): Promise<void> {
  try {
    state.selectedGameId = gameId;
    state.selectedLeaderboardId = leaderboardId;
    state.page = page;
    state.leaderboardData = undefined;
    state.loading = true;
    state.view = 'leaderboard';
    saveUiState();
    renderApp();
    const data = await fetchLeaderboardEntries(gameId, leaderboardId, page, 100);
    state.leaderboardData = data;
    state.sortDir = data.sortOrder === 'asc' ? 'asc' : 'desc';
    state.sortKey = 'score';
  } catch (error) {
    state.authMessage = (error as Error).message || 'Unable to load leaderboard';
  } finally {
    state.loading = false;
    renderApp();
  }
}

async function registerGame(companyId: string, companySecret: string, name: string): Promise<GameSummary> {
  const res = await fetch(`${API_BASE}/studio/games`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ company_id: companyId, company_secret: companySecret, name })
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || 'Unable to create game');
  }
  const data = await res.json();
  return { game_id: data.game_id, name: data.name, leaderboards: [] };
}

async function registerLeaderboard(
  companyId: string,
  companySecret: string,
  gameId: string,
  leaderboardId: string,
  name: string
): Promise<LeaderboardSummary> {
  const res = await fetch(`${API_BASE}/studio/leaderboards`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      company_id: companyId,
      company_secret: companySecret,
      game_id: gameId,
      leaderboard_id: leaderboardId,
      name
    })
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || 'Unable to create leaderboard');
  }
  const data = await res.json();
  return { leaderboard_id: data.leaderboard_id, name: data.name, sort_order: data.sort_order };
}

function renderWelcome(): void {
  app.innerHTML = `
    <div class="topbar">
      <div class="brand">
        <div class="brand-badge">LX</div>
        <span>LeaderboardX Console</span>
      </div>
      <div class="user-chip">Backend-connected console</div>
    </div>
    <div class="hero">
      <h1>Operate leaderboards like Firebase, but for games.</h1>
      <p>
        Log in or sign up to manage studios, games, and leaderboards. No email is required — we keep it lightweight for rapid iteration.
        Uses backend APIs for real data; credentials are your Studio (company) ID and secret.
      </p>
      <div class="actions">
        <button class="btn primary" id="login-btn">Log in</button>
        <button class="btn" id="signup-btn">Sign up</button>
      </div>
    </div>
  `;

  app.querySelector('#login-btn')?.addEventListener('click', () => {
    state.view = 'login';
    renderApp();
  });

  app.querySelector('#signup-btn')?.addEventListener('click', () => {
    state.view = 'signup';
    renderApp();
  });
}

function renderAuth(mode: 'login' | 'signup'): void {
  app.innerHTML = `
    <div class="topbar">
      <div class="brand">
        <div class="brand-badge">LX</div>
        <span>${mode === 'login' ? 'Log in' : 'Create a studio account'}</span>
      </div>
      <button class="btn ghost" id="back-home">Back</button>
    </div>
    <div class="page">
      <div class="hero" style="max-width: 520px;">
        <h1>${mode === 'login' ? 'Welcome back' : 'Create your studio space'}</h1>
        <p>Use your Studio (company) ID and secret to access the console.</p>
        <p class="text-muted" style="margin-bottom: 12px;">Don't have one? Sign up to generate a company ID + secret.</p>
        <form id="auth-form">
          <div class="input-group">
            <label for="companyId">Company ID</label>
            <input required name="companyId" id="companyId" placeholder="UUID from signup" />
          </div>
          <div class="input-group">
            <label for="secret">Company Secret</label>
            <input required type="password" name="secret" id="secret" placeholder="••••••••" />
          </div>
          ${
            mode === 'signup'
              ? `<div class="input-group">
                  <label for="companyName">Studio name</label>
                  <input required name="companyName" id="companyName" placeholder="Neon Storm Studios" />
                </div>`
              : ''
          }
          <div class="actions">
            <button class="btn primary" type="submit">${mode === 'login' ? 'Log in' : 'Sign up'}</button>
            <button class="btn ghost" type="button" id="swap-mode">${
              mode === 'login' ? 'Need an account?' : 'Have an account? Log in'
            }</button>
          </div>
          ${state.authMessage ? `<p style="color: var(--danger); margin-top: 12px;">${state.authMessage}</p>` : ''}
        </form>
      </div>
    </div>
  `;

  app.querySelector('#back-home')?.addEventListener('click', () => {
    state.view = 'welcome';
    renderApp();
  });

  app.querySelector('#swap-mode')?.addEventListener('click', () => {
    state.authMessage = undefined;
    state.view = mode === 'login' ? 'signup' : 'login';
    renderApp();
  });

  app.querySelector('#auth-form')?.addEventListener('submit', (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget as HTMLFormElement);
    const companyId = (formData.get('companyId') || '').toString().trim();
    const secret = (formData.get('secret') || '').toString().trim();
    if (!companyId || !secret) {
      state.authMessage = 'Company ID and secret are required.';
      renderApp();
      return;
    }

    if (mode === 'signup') {
      const companyName = (formData.get('companyName') || '').toString().trim();
      if (!companyName) {
        state.authMessage = 'Studio name is required.';
        renderApp();
        return;
      }
      handleSignup(companyName);
    } else {
      handleLogin(companyId, secret);
    }
  });
}

async function handleLogin(companyId: string, secret: string): Promise<void> {
  try {
    state.loading = true;
    renderApp();
    const studio = await fetchCompanySummary(companyId, secret);
    state.studio = studio;
    state.session = { companyId, companySecret: secret, expiresAt: Date.now() + SESSION_TTL_MS };
    saveSession(state.session);
    state.authMessage = undefined;
    state.view = 'studio';
    state.selectedGameId = undefined;
    state.selectedLeaderboardId = undefined;
    state.leaderboardData = undefined;
    saveUiState();
  } catch (error) {
    state.authMessage = (error as Error).message || 'Login failed';
  } finally {
    state.loading = false;
    renderApp();
  }
}

async function handleSignup(companyName: string): Promise<void> {
  try {
    state.loading = true;
    renderApp();
    const created = await registerCompany(companyName);
    // After signup, log them in using the returned credentials
    await handleLogin(created.company_id, created.company_secret);
  } catch (error) {
    state.authMessage = (error as Error).message || 'Signup failed';
    state.loading = false;
    renderApp();
  }
}

function renderShell(content: string, active: 'studio' | 'game'): void {
  const userLabel = state.session ? `Company: ${state.session.companyId}` : 'Guest';
  const tree = buildSidebarTree();
  app.innerHTML = `
    <div class="topbar">
      <div class="brand">
        <div class="brand-badge">LX</div>
        <span>${state.studio?.name || 'Studio Console'}</span>
      </div>
      <div class="user-chip">${userLabel}</div>
    </div>
    <div class="shell">
      <aside class="sidebar">
        <div class="sidebar-header nav-item ${active === 'studio' ? 'active' : ''}" data-nav="studio">
          <span>Studio Overview</span>
          <button class="btn icon large" id="settings-btn" title="Settings">⚙</button>
        </div>
        <div class="tree">${tree}</div>
      </aside>
      <main class="page">${content}</main>
    </div>
  `;

  app.querySelectorAll<HTMLElement>('.nav-item').forEach((item) => {
    item.addEventListener('click', () => {
      const nav = item.dataset.nav;
      if (nav === 'studio') {
        navigate('studio', { push: true });
      } else if (nav === 'game') {
        state.selectedLeaderboardId = undefined;
        navigate('game', { push: true });
      }
    });
  });
  const settingsBtn = app.querySelector('#settings-btn');
  settingsBtn?.addEventListener('click', () => navigate('settings', { push: true }));
  bindSidebarTree();
}

function renderStudioDashboard(): void {
  if (!state.studio) {
    state.view = 'welcome';
    renderApp();
    return;
  }
  const games = state.studio.games || [];
  const totalLeaderboards = games.reduce((acc, game) => acc + game.leaderboards.length, 0);
  const content = `
    <div class="section-header">
      <div>
        <div class="badge">Studios</div>
        <h2 style="margin: 8px 0 0;">${state.studio.name}</h2>
        <p class="text-muted">Manage every game and leaderboard from a Firebase-inspired console.</p>
      </div>
      <div class="actions">
        <button class="btn primary" id="new-game-btn">Register new game</button>
      </div>
    </div>
    <div class="card-grid">
      ${games
        .map(
          (game) => `
            <div class="card">
              <div class="badge">Game</div>
              <h3>${game.name}</h3>
              <p>${game.leaderboards.length} leaderboards</p>
              <div class="actions" style="margin-top: 12px;">
                <button class="btn primary" data-game="${game.game_id}">Open dashboard</button>
              </div>
            </div>
          `
        )
        .join('')}
    </div>
    <div class="card" style="margin-top: 16px;">
      <h3>Studio Overview</h3>
      <p>Total games: <strong>${games.length}</strong></p>
      <p>Total leaderboards: <strong>${totalLeaderboards}</strong></p>
      <p class="text-muted">All values shown are demo data; hook up the backend API to view live stats.</p>
    </div>
  `;

  renderShell(content, 'studio');

  app.querySelector('#new-game-btn')?.addEventListener('click', () => openNewGamePrompt());
  app.querySelectorAll<HTMLButtonElement>('button[data-game]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.selectedGameId = btn.dataset.game;
      state.selectedLeaderboardId = undefined;
      state.page = 1;
      state.view = 'game';
      saveUiState();
      renderApp();
    });
  });

  bindSidebarTree();
}

function openNewGamePrompt(): void {
  if (!state.session || !state.studio) {
    state.authMessage = 'Log in to create games.';
    renderApp();
    return;
  }
  const name = prompt('Game name');
  if (!name) return;
  state.loading = true;
  renderApp();
  registerGame(state.session.companyId, state.session.companySecret, name)
    .then(async (game) => {
      // Refresh from backend to ensure DB state is reflected
      const refreshed = await fetchCompanySummary(state.session!.companyId, state.session!.companySecret);
      state.studio = refreshed;
      state.selectedGameId = game.game_id;
      state.view = 'game';
      saveUiState();
    })
    .catch((e) => {
      state.authMessage = (e as Error).message || 'Unable to create game';
    })
    .finally(() => {
      state.loading = false;
      renderApp();
    });
}

function renderGameDashboard(): void {
  if (!state.studio) {
    state.view = 'welcome';
    renderApp();
    return;
  }
  const game = state.studio.games.find((g) => g.game_id === state.selectedGameId) || state.studio.games[0];
  if (!game) {
    state.view = 'studio';
    renderApp();
    return;
  }
  state.selectedGameId = game.game_id;

  const content = `
    <div class="section-header">
      <div>
        <div class="badge">Game</div>
        <h2 style="margin: 8px 0 4px;">${game.name}</h2>
        <p class="text-muted">Studio › ${state.studio.name} · ${game.leaderboards.length} leaderboards</p>
      </div>
      <div class="actions">
        <button class="btn" id="simulate-player-btn">Simulate player</button>
        <button class="btn icon large" id="game-settings-btn" title="Rename game">✎</button>
      </div>
    </div>
    <div class="card-grid">
      ${game.leaderboards
        .map(
          (lb) => `
            <div class="card">
              <div class="badge">Leaderboard</div>
              <h3>${lb.name || lb.leaderboard_id}</h3>
              <p>Sort: ${lb.sort_order.toUpperCase()}</p>
              <div class="actions" style="margin-top: 12px;">
                <button class="btn primary" data-lb="${lb.leaderboard_id}">Open dashboard</button>
              </div>
            </div>
          `
        )
        .join('')}
    </div>
    <div class="card" style="margin-top: 16px;">
      <h3>Simulate player</h3>
      <p class="text-muted" style="margin-bottom: 12px;">Quickly test player behaviour (submits scores, creates leaderboards on first submit).</p>
      <div class="actions" style="flex-wrap: wrap;">
        <button class="btn" id="simulate-player-btn">Simulate player</button>
      </div>
    </div>
  `;

  renderShell(content, 'game');

  app.querySelectorAll<HTMLButtonElement>('button[data-lb]').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (!btn.dataset.lb) return;
      openLeaderboard(game.game_id, btn.dataset.lb, 1);
    });
  });

  app.querySelector('#simulate-player-btn')?.addEventListener('click', () => {
    navigate('playerLogin', { gameId: game.game_id, push: true });
  });

  app.querySelector('#game-settings-btn')?.addEventListener('click', () => {
    const newName = prompt('New game name', game.name);
    if (!newName || !state.session) return;
    game.name = newName;
    renderApp();
  });
}

function renderPlayerLoginPage(): void {
  if (!state.studio) {
    navigate('welcome', { push: false });
    return;
  }
  const game =
    state.studio.games.find((g) => g.game_id === state.selectedGameId) || state.studio.games[0];
  if (!game) {
    navigate('studio', { push: false });
    return;
  }
  state.selectedGameId = game.game_id;
  const deviceId = state.playerSession?.deviceId || '';
  const playerMessage = state.playerMessage || '';

  const content = `
    <div class="section-header">
      <div>
        <div class="badge">Player login</div>
        <h2 style="margin: 8px 0 4px;">${game.name}</h2>
        <p class="text-muted">Authenticate a simulated player device. Use browser back to return.</p>
      </div>
      <div class="actions">
        <button class="btn ghost" id="back-game">Back to game</button>
      </div>
    </div>
    <div class="panel" style="max-width:560px;">
      <div class="input-group">
        <label>Device ID</label>
        <div style="display:flex; gap:8px;">
          <input id="device-id-input" value="${deviceId}" placeholder="device-123" />
          <button class="btn" id="gen-device">Generate</button>
        </div>
      </div>
      <div class="actions">
        <button class="btn primary" id="player-login-btn">Login as player</button>
      </div>
      ${playerMessage ? `<p class="text-muted">${playerMessage}</p>` : ''}
    </div>
  `;

  renderShell(content, 'game');

  app.querySelector('#back-game')?.addEventListener('click', () => {
    navigate('game', { push: true });
  });

  app.querySelector('#gen-device')?.addEventListener('click', () => {
    const newId = `device-${Math.random().toString(36).slice(2, 8)}`;
    (app.querySelector('#device-id-input') as HTMLInputElement | null)!.value = newId;
  });

  app.querySelector('#player-login-btn')?.addEventListener('click', async () => {
    const devInput = app.querySelector('#device-id-input') as HTMLInputElement | null;
    const deviceIdVal = (devInput?.value || '').trim();
    if (!deviceIdVal) {
      alert('Enter a device ID');
      return;
    }
    try {
      state.loading = true;
      renderShell(content, 'game');
      const res = await clientAuth(game.game_id, deviceIdVal);
      state.playerSession = { deviceId: deviceIdVal, xid: res.xid };
      state.playerMessage = res.is_new ? 'New player created.' : 'Player session restored.';
      if (!state.selectedLeaderboardId && game.leaderboards.length > 0) {
        state.selectedLeaderboardId = game.leaderboards[0].leaderboard_id;
      }
      navigate('playerSim', { push: true });
      if (state.selectedLeaderboardId) {
        loadPreviewLeaderboard(game.game_id, state.selectedLeaderboardId);
      }
    } catch (e) {
      state.playerMessage = (e as Error).message;
    } finally {
      state.loading = false;
      renderApp();
    }
  });
}

function renderPlayerSimulatorPage(): void {
  if (!state.studio) {
    navigate('welcome', { push: false });
    return;
  }
  const game =
    state.studio.games.find((g) => g.game_id === state.selectedGameId) || state.studio.games[0];
  if (!game) {
    navigate('studio', { push: false });
    return;
  }
  if (!state.playerSession?.xid) {
    navigate('playerLogin', { gameId: game.game_id, push: true });
    return;
  }
  state.selectedGameId = game.game_id;
  const leaderboards = game.leaderboards;
  if (!state.selectedLeaderboardId && leaderboards.length > 0) {
    state.selectedLeaderboardId = leaderboards[0].leaderboard_id;
  }
  const deviceId = state.playerSession.deviceId;
  const xid = state.playerSession.xid;
  const playerMessage = state.playerMessage || '';
  const leaderboardData =
    state.leaderboardData?.leaderboardId === state.selectedLeaderboardId ? state.leaderboardData : undefined;

  const content = `
    <div class="section-header">
      <div>
        <div class="badge">Player simulator</div>
        <h2 style="margin: 8px 0 4px;">${game.name}</h2>
        <p class="text-muted">Simulated player session is active. Use browser back to return.</p>
        <p class="text-muted">Device: ${deviceId} · XID: ${xid}</p>
      </div>
      <div class="actions">
        <button class="btn ghost" id="back-game">Back to game</button>
        <button class="btn" id="logout-player-btn" ${xid ? '' : 'disabled'}>Logout player</button>
        <button class="btn ghost" id="switch-player-btn">Switch player</button>
      </div>
    </div>
    <div class="panel" style="margin-bottom:14px;">
      <h3>Leaderboard + Score</h3>
      <div class="input-group">
        <label>Leaderboard ID</label>
        <select id="sim-lb-select">
          ${(leaderboards || [])
            .map(
              (lb) =>
                `<option value="${lb.leaderboard_id}" ${
                  lb.leaderboard_id === state.selectedLeaderboardId ? 'selected' : ''
                }>${lb.name || lb.leaderboard_id}</option>`
            )
            .join('')}
        </select>
        <button class="btn" id="new-sim-lb-btn" style="margin-top:8px;">Create new leaderboard ID</button>
      </div>
      <div class="input-group">
        <label>Score value</label>
        <input id="score-input" type="number" placeholder="5000" />
      </div>
      <div class="actions">
        <button class="btn primary" id="submit-score-btn" ${!xid ? 'disabled' : ''}>Submit score</button>
      </div>
      ${playerMessage ? `<p class="text-muted">${playerMessage}</p>` : ''}
    </div>
    <div class="panel">
      <h3>Leaderboard preview</h3>
      <p class="text-muted">Top scores for ${state.selectedLeaderboardId || ''}</p>
      ${
        leaderboardData && leaderboardData.entries.length > 0
          ? `<div class="table-wrapper" style="box-shadow:none;">
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>XID</th>
                    <th>Score</th>
                    <th>Updated</th>
                  </tr>
                </thead>
                <tbody>
                  ${leaderboardData.entries
                    .slice(0, 10)
                    .map(
                      (entry, idx) => `
                        <tr>
                          <td>${idx + 1}</td>
                          <td>${entry.xid}</td>
                          <td>${entry.score.toLocaleString()}</td>
                          <td>${formatDate(entry.updatedOn)}</td>
                        </tr>
                      `
                    )
                    .join('')}
                </tbody>
              </table>
            </div>`
          : `<p class="text-muted">No scores yet.</p>`
      }
    </div>
  `;

  renderShell(content, 'game');

  // Default selection fetch
  if (state.selectedLeaderboardId && (!state.leaderboardData || state.leaderboardData.leaderboardId !== state.selectedLeaderboardId)) {
    loadPreviewLeaderboard(game.game_id, state.selectedLeaderboardId);
  }

  app.querySelector('#back-game')?.addEventListener('click', () => {
    navigate('game', { push: true });
  });

  app.querySelector('#logout-player-btn')?.addEventListener('click', () => {
    state.playerSession = undefined;
    state.playerMessage = undefined;
    navigate('playerLogin', { gameId: game.game_id, push: true });
  });

  app.querySelector('#switch-player-btn')?.addEventListener('click', () => {
    navigate('playerLogin', { gameId: game.game_id, push: true });
  });

  app.querySelector('#new-sim-lb-btn')?.addEventListener('click', () => {
    const name = prompt('Enter new leaderboard ID (a-z, 0-9, -):');
    if (!name) return;
    if (!/^[a-z0-9-]+$/.test(name)) {
      alert('Leaderboard ID must use a-z, 0-9, and hyphen.');
      return;
    }
    state.selectedLeaderboardId = name;
    // Push to dropdown immediately
    game.leaderboards = [...game.leaderboards, { leaderboard_id: name, name, sort_order: 'desc' }];
    loadPreviewLeaderboard(game.game_id, name).then(() => renderPlayerSimulatorPage());
  });

  app.querySelector('#sim-lb-select')?.addEventListener('change', (e) => {
    const lbId = (e.target as HTMLSelectElement).value;
    state.selectedLeaderboardId = lbId;
    loadPreviewLeaderboard(game.game_id, lbId).then(() => renderPlayerSimulatorPage());
  });

  app.querySelector('#submit-score-btn')?.addEventListener('click', async () => {
    if (!state.playerSession?.xid) {
      state.playerMessage = 'Log in a player first.';
      renderPlayerSimulatorPage();
      return;
    }
    const lbId = state.selectedLeaderboardId || (app.querySelector('#sim-lb-select') as HTMLSelectElement | null)?.value;
    if (!lbId) {
      state.playerMessage = 'Select a leaderboard.';
      renderPlayerSimulatorPage();
      return;
    }
    const rawVal = (app.querySelector('#score-input') as HTMLInputElement | null)?.value;
    const scoreVal = rawVal !== undefined && rawVal !== null && rawVal !== '' ? Number(rawVal) : NaN;
    if (!Number.isFinite(scoreVal)) {
      state.playerMessage = 'Enter a valid score (integer or decimal).';
      renderPlayerSimulatorPage();
      return;
    }
    try {
      state.loading = true;
      renderPlayerSimulatorPage();
      await clientSubmitScore(game.game_id, lbId, state.playerSession.xid!, scoreVal);
      state.playerMessage = 'Score submitted.';
      await loadPreviewLeaderboard(game.game_id, lbId);
    } catch (e) {
      state.playerMessage = (e as Error).message;
    } finally {
      state.loading = false;
      renderPlayerSimulatorPage();
    }
  });

  app.querySelector('#view-lb-btn')?.addEventListener('click', () => {
    const lbId = state.selectedLeaderboardId || (app.querySelector('#sim-lb-select') as HTMLSelectElement | null)?.value;
    if (!lbId) {
      alert('Select a leaderboard.');
      return;
    }
    openLeaderboard(game.game_id, lbId, 1);
  });

  const scoreInput = app.querySelector('#score-input') as HTMLInputElement | null;
  const submitBtn = app.querySelector('#submit-score-btn') as HTMLButtonElement | null;
  if (scoreInput && submitBtn) {
    const toggleSubmit = () => {
      const raw = scoreInput.value;
      const num = raw !== '' ? Number(raw) : NaN;
      const valid = Number.isFinite(num);
      submitBtn.disabled = !state.playerSession?.xid || !valid;
    };
    scoreInput.addEventListener('input', toggleSubmit);
    toggleSubmit();
  }
}

function renderSettings(): void {
  if (!state.session || !state.studio) {
    navigate('welcome', { push: true });
    return;
  }
  const content = `
    <div class="section-header">
      <div>
        <div class="badge">Settings</div>
        <h2 style="margin: 8px 0 4px;">${state.studio.name}</h2>
        <p class="text-muted">Manage studio settings and access.</p>
      </div>
    </div>
    <div class="panel" style="max-width:600px;">
      <h3>Studio name</h3>
      <div class="input-group">
        <label>Display name</label>
        <input id="studio-name-input" value="${state.studio.name}" />
      </div>
      <div class="actions">
        <button class="btn primary" id="save-name-btn" disabled>Save (not wired)</button>
      </div>
      <p class="text-muted">Renaming requires backend support; UI placeholder only.</p>
    </div>
    <div class="panel" style="max-width:600px;">
      <h3>Studio secret / password</h3>
      <p class="text-muted">Password/secret rotation should be done via backend API. Placeholder only.</p>
      <div class="actions">
        <button class="btn primary" id="rotate-secret-btn" disabled>Rotate secret (not wired)</button>
      </div>
    </div>
    <div class="panel" style="max-width:600px;">
      <h3>Logout</h3>
      <div class="actions">
        <button class="btn" id="logout-btn">Logout of console</button>
      </div>
    </div>
  `;
  renderShell(content, 'studio');
  app.querySelector('#logout-btn')?.addEventListener('click', () => handleLogout());
}

function renderPlayerModal(): string {
  return '';
}

function bindPlayerModal(): void {
  return;
}

function resolveFilterRange(filter: FilterState): { start?: number; end?: number } {
  const end = Date.now();
  switch (filter.kind) {
    case '1h':
      return { start: end - 60 * 60 * 1000, end };
    case '6h':
      return { start: end - 6 * 60 * 60 * 1000, end };
    case '24h':
      return { start: end - 24 * 60 * 60 * 1000, end };
    case '48h':
      return { start: end - 48 * 60 * 60 * 1000, end };
    case 'custom': {
      const start = filter.start ? new Date(filter.start).getTime() : undefined;
      const customEnd = filter.end ? new Date(filter.end).getTime() : undefined;
      return { start, end: customEnd };
    }
    default:
      return {};
  }
}

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat('en', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(iso));
}

function sortEntries(entries: ScoreEntry[]): ScoreEntry[] {
  const sorted = [...entries];
  const direction = state.sortDir === 'asc' ? 1 : -1;
  sorted.sort((a, b) => {
    const key = state.sortKey;
    if (key === 'score') return (a.score - b.score) * direction;
    if (key === 'updatedOn') return (new Date(a.updatedOn).getTime() - new Date(b.updatedOn).getTime()) * direction;
    return a.xid.localeCompare(b.xid) * direction;
  });
  return sorted;
}

function renderLeaderboardDashboard(): void {
  if (!state.studio) {
    state.view = 'welcome';
    renderApp();
    return;
  }
  const game = state.studio.games.find((g) => g.game_id === state.selectedGameId) || state.studio.games[0];
  if (!game) {
    state.view = 'studio';
    renderApp();
    return;
  }
  const leaderboard =
    game.leaderboards.find((lb) => lb.leaderboard_id === state.selectedLeaderboardId) || game.leaderboards[0];
  if (!leaderboard) {
    state.view = 'game';
    renderApp();
    return;
  }
  const leaderboardOptions: LeaderboardOption[] = game.leaderboards.map((lb) => ({
    leaderboard_id: lb.leaderboard_id,
    name: lb.name,
    sort_order: lb.sort_order,
  }));
  state.selectedGameId = game.game_id;
  state.selectedLeaderboardId = leaderboard.leaderboard_id;
  saveUiState();

  if (!state.leaderboardData && !state.loading) {
    openLeaderboard(game.game_id, leaderboard.leaderboard_id, state.page);
    return;
  }

  const pageSize = 100;
  const leaderboardData =
    state.leaderboardData?.leaderboardId === leaderboard.leaderboard_id ? state.leaderboardData : undefined;
  const { start, end } = resolveFilterRange(state.filter);
  const filtered = (leaderboardData?.entries || []).filter((entry) => {
    const ts = new Date(entry.updatedOn).getTime();
    if (start && ts < start) return false;
    if (end && ts > end) return false;
    return true;
  });

  const sorted = sortEntries(filtered);
  const totalPages = Math.max(1, Math.ceil((leaderboardData?.total || sorted.length) / pageSize));
  const currentPage = Math.min(state.page, totalPages);
  const paginated = sorted;

  const content = `
    <div class="section-header">
      <div>
        <div class="badge">Leaderboard</div>
        <h2 style="margin: 8px 0 4px;">${leaderboard.name || leaderboard.leaderboard_id}</h2>
        <p class="text-muted">Studio › ${state.studio.name} · Game › ${game.name}</p>
        <p class="text-muted">Sort: ${leaderboard.sort_order.toUpperCase()}</p>
      </div>
      <div class="actions">
        <button class="btn ghost" id="back-game">Back to game</button>
      </div>
    </div>
    <div class="panel" style="margin-bottom: 14px;">
      <div class="split">
        <div>
          <div class="input-group">
            <label>Leaderboard</label>
            <select id="lb-select">
              ${leaderboardOptions
                .map(
                  (lb) =>
                    `<option value="${lb.leaderboard_id}" ${lb.leaderboard_id === leaderboard.leaderboard_id ? 'selected' : ''}>${
                      lb.name || lb.leaderboard_id
                    }</option>`
                )
                .join('')}
            </select>
          </div>
          <div class="actions">
            <button class="btn" id="new-lb-btn">Create new leaderboard ID</button>
          </div>
        </div>
        <div>
          <div class="badge">Player simulator</div>
          ${state.playerSession?.xid ? `<p class="text-muted">Device: ${state.playerSession.deviceId} · XID: ${state.playerSession.xid}</p>` : '<p class="text-muted">Authenticate a player in the game view.</p>'}
        </div>
      </div>
    </div>
    <div class="toolbar" style="position: relative;">
      <div class="filters">
        <button class="btn" id="filter-toggle">Filter</button>
        <div class="badge">${renderFilterLabel(state.filter)}</div>
      </div>
      <div class="actions">
        <button class="btn ghost" id="refresh-btn">Refresh data</button>
      </div>
      ${state.filterOpen ? renderFilterPanel() : ''}
    </div>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            ${renderHeaderCell('xid', 'XID')}
            ${renderHeaderCell('score', 'Score')}
            ${renderHeaderCell('updatedOn', 'Updated on')}
          </tr>
        </thead>
        <tbody>
          ${
            state.loading && !leaderboardData
              ? `<tr><td colspan="3" class="empty-state">Loading leaderboard...</td></tr>`
              : paginated.length === 0
                  ? `<tr><td colspan="3" class="empty-state">No scores for this range yet.</td></tr>`
                  : paginated
                      .map(
                        (entry) => `
                          <tr>
                            <td>${entry.xid}</td>
                            <td><strong>${entry.score.toLocaleString()}</strong></td>
                            <td>${formatDate(entry.updatedOn)}</td>
                          </tr>
                        `
                      )
                      .join('')
          }
        </tbody>
      </table>
      <div class="pagination">
        <span>Showing ${paginated.length} of ${leaderboardData?.total ?? paginated.length} · Page ${currentPage}/${totalPages}</span>
        <button class="btn icon" id="prev-page" ${currentPage === 1 ? 'disabled' : ''}>◀</button>
        <button class="btn icon" id="next-page" ${currentPage === totalPages ? 'disabled' : ''}>▶</button>
      </div>
    </div>
  `;

  renderShell(content, 'game');

  app.querySelector('#back-game')?.addEventListener('click', () => {
    state.view = 'game';
    saveUiState();
    renderApp();
  });

  app.querySelector('#lb-select')?.addEventListener('change', (e) => {
    const lbId = (e.target as HTMLSelectElement).value;
    if (!lbId) return;
    openLeaderboard(game.game_id, lbId, 1);
  });

  app.querySelector('#new-lb-btn')?.addEventListener('click', () => {
    const name = prompt('Enter new leaderboard ID (a-z, 0-9, -):');
    if (!name) return;
    if (!/^[a-z0-9-]+$/.test(name)) {
      alert('Leaderboard ID must use a-z, 0-9, and hyphen.');
      return;
    }
    openLeaderboard(game.game_id, name, 1);
  });

  app.querySelector('#filter-toggle')?.addEventListener('click', () => {
    state.filterOpen = !state.filterOpen;
    renderApp();
  });

  app.querySelector('#refresh-btn')?.addEventListener('click', () => {
    openLeaderboard(game.game_id, leaderboard.leaderboard_id, state.page);
  });

  app.querySelector('#prev-page')?.addEventListener('click', () => {
    if (currentPage === 1) return;
    openLeaderboard(game.game_id, leaderboard.leaderboard_id, currentPage - 1);
  });
  app.querySelector('#next-page')?.addEventListener('click', () => {
    if (currentPage === totalPages) return;
    openLeaderboard(game.game_id, leaderboard.leaderboard_id, currentPage + 1);
  });

  app.querySelectorAll<HTMLElement>('th[data-sort]').forEach((th) => {
    th.addEventListener('click', () => {
      const key = th.dataset.sort as SortKey;
      if (state.sortKey === key) {
        state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
      } else {
        state.sortKey = key;
        state.sortDir = key === 'score' ? 'desc' : 'asc';
      }
      renderApp();
    });
  });

  bindFilterPanel();
}

function renderHeaderCell(key: SortKey, label: string): string {
  const active = state.sortKey === key;
  const arrow = active ? (state.sortDir === 'asc' ? '↑' : '↓') : '';
  return `<th data-sort="${key}">${label} ${arrow}</th>`;
}

function renderFilterLabel(filter: FilterState): string {
  switch (filter.kind) {
    case '1h':
      return 'Last 1 hour';
    case '6h':
      return 'Last 6 hours';
    case '24h':
      return 'Last 24 hours';
    case '48h':
      return 'Last 48 hours';
    case 'custom':
      return `Custom: ${filter.start || '?'} → ${filter.end || '?'}`;
    default:
      return 'All time';
  }
}

function renderFilterPanel(): string {
  return `
    <div class="filter-panel">
      <div class="filter-options">
        ${renderFilterButton('1h', 'Last 1 hour')}
        ${renderFilterButton('6h', 'Last 6 hours')}
        ${renderFilterButton('24h', 'Last 24 hours')}
        ${renderFilterButton('48h', 'Last 48 hours')}
        <div class="card" style="box-shadow:none; border:1px dashed var(--border);">
          <strong>Custom range</strong>
          <div class="calendar">
            <div class="input-group">
              <label>Start</label>
              <input type="date" id="custom-start" value="${state.filter.start || ''}" />
            </div>
            <div class="input-group">
              <label>End</label>
              <input type="date" id="custom-end" value="${state.filter.end || ''}" />
            </div>
          </div>
          <div class="actions" style="margin-top: 10px;">
            <button class="btn primary" id="apply-custom">Apply</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderFilterButton(kind: FilterKind, label: string): string {
  const active = state.filter.kind === kind;
  return `<button class="btn ${active ? 'primary' : ''}" data-filter="${kind}">${label}</button>`;
}

function bindFilterPanel(): void {
  if (!state.filterOpen) return;
  app.querySelectorAll<HTMLButtonElement>('button[data-filter]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const kind = btn.dataset.filter as FilterKind;
      state.filter = { kind };
      state.page = 1;
      state.filterOpen = false;
      if (state.view === 'leaderboard' && state.selectedGameId && state.selectedLeaderboardId) {
        openLeaderboard(state.selectedGameId, state.selectedLeaderboardId, 1);
        return;
      }
      renderApp();
    });
  });

  app.querySelector('#apply-custom')?.addEventListener('click', () => {
    const start = (app.querySelector('#custom-start') as HTMLInputElement | null)?.value;
    const end = (app.querySelector('#custom-end') as HTMLInputElement | null)?.value;
    state.filter = { kind: 'custom', start: start || undefined, end: end || undefined };
    state.page = 1;
    state.filterOpen = false;
    if (state.view === 'leaderboard' && state.selectedGameId && state.selectedLeaderboardId) {
      openLeaderboard(state.selectedGameId, state.selectedLeaderboardId, 1);
      return;
    }
    renderApp();
  });
}

async function bootstrap(): Promise<void> {
  const savedSession = loadSession();
  const urlState = readUrlState();
  const ui = loadUiState();
  window.onpopstate = () => {
    const popped = readUrlState();
    state.view = popped.view || 'welcome';
    state.selectedGameId = popped.selectedGameId;
    state.selectedLeaderboardId = popped.selectedLeaderboardId;
    // if playerSim requested but no player session, send to playerLogin
    if (state.view === 'playerSim' && !state.playerSession) {
      state.view = 'playerLogin';
    }
    renderApp();
  };
  if (savedSession) {
    try {
      state.loading = true;
      state.session = savedSession;
      const studio = await fetchCompanySummary(savedSession.companyId, savedSession.companySecret);
      state.studio = studio;
      state.view = urlState.view || ui.view || 'studio';
      state.selectedGameId = urlState.selectedGameId || ui.selectedGameId;
      state.selectedLeaderboardId = urlState.selectedLeaderboardId || ui.selectedLeaderboardId;
      if (state.view === 'leaderboard' && state.selectedGameId && state.selectedLeaderboardId) {
        await openLeaderboard(state.selectedGameId, state.selectedLeaderboardId, state.page || 1);
        return;
      }
    } catch (error) {
      state.authMessage = (error as Error).message;
      clearSession();
      state.session = undefined;
    } finally {
      state.loading = false;
    }
  } else {
    const { view } = urlState;
    if (view === 'login' || view === 'signup') {
      state.view = view;
    }
  }
  renderApp();
}

bootstrap();
function bindSidebarTree(): void {
  const gameToggles = app.querySelectorAll<HTMLElement>('.tree-row[data-type="game"]');
  gameToggles.forEach((row) => {
    row.addEventListener('click', () => {
      const gameId = row.dataset.game;
      if (!gameId || !state.studio) return;
      const current = state.expandedGames?.[gameId] ?? gameId === state.selectedGameId;
      state.expandedGames = { ...(state.expandedGames || {}), [gameId]: !current };
      state.selectedGameId = gameId;
      navigate('game', { gameId, push: true });
    });
  });

  const lbNodes = app.querySelectorAll<HTMLElement>('.tree-leaf[data-type="leaderboard"]');
  lbNodes.forEach((leaf) => {
    leaf.addEventListener('click', () => {
      const gameId = leaf.dataset.game;
      const lbId = leaf.dataset.lb;
      if (!gameId || !lbId) return;
      navigate('leaderboard', { gameId, leaderboardId: lbId, push: true });
    });
  });
}
