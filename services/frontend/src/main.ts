type View = 'welcome' | 'login' | 'signup' | 'studio' | 'game' | 'leaderboard';

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
  entries: ScoreEntry[];
  total: number;
  sortOrder: 'asc' | 'desc';
}

interface Session {
  companyId: string;
  companySecret: string;
  expiresAt: number;
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
  loading: false
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
  }
}

function saveSession(session: Session): void {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

function clearSession(): void {
  localStorage.removeItem(SESSION_KEY);
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
    entries: (data.entries || []).map((e: any) => ({
      xid: e.xid,
      score: e.best_value,
      updatedOn: e.updated_at
    })),
    total: data.total,
    sortOrder: data.sort_order
  };
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
        <h4>Spaces</h4>
        <div class="nav-item ${active === 'studio' ? 'active' : ''}" data-nav="studio">Studio overview</div>
        <div class="nav-item ${active === 'game' ? 'active' : ''}" data-nav="game">Games</div>
        <h4>Actions</h4>
        <div class="nav-item" data-nav="logout">Logout</div>
      </aside>
      <main class="page">${content}</main>
    </div>
  `;

  app.querySelectorAll<HTMLElement>('.nav-item').forEach((item) => {
    item.addEventListener('click', () => {
      const nav = item.dataset.nav;
      if (nav === 'logout') {
        state.session = undefined;
        state.studio = undefined;
        state.selectedGameId = undefined;
        state.selectedLeaderboardId = undefined;
        state.leaderboardData = undefined;
        clearSession();
        localStorage.removeItem(UI_STATE_KEY);
        state.view = 'welcome';
        saveUiState();
        renderApp();
        return;
      }
      if (nav === 'studio') {
        state.view = 'studio';
      } else if (nav === 'game') {
        state.selectedLeaderboardId = undefined;
        state.view = 'game';
      }
      saveUiState();
      renderApp();
    });
  });
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
      <h3>Overview</h3>
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
        <button class="btn ghost" id="back-studio">Back to studio</button>
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
      <h3>Create new leaderboard</h3>
      <p style="margin-bottom: 12px;">Spin up a board instantly; a unique ID is generated for you.</p>
      <div class="actions">
        <button class="btn" id="new-lb-btn">Add leaderboard</button>
      </div>
    </div>
  `;

  renderShell(content, 'game');

  app.querySelector('#back-studio')?.addEventListener('click', () => {
    state.view = 'studio';
    renderApp();
  });

  app.querySelectorAll<HTMLButtonElement>('button[data-lb]').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (!btn.dataset.lb) return;
      openLeaderboard(game.game_id, btn.dataset.lb, 1);
    });
  });

  app.querySelector('#new-lb-btn')?.addEventListener('click', () => {
    const name = prompt('Leaderboard name');
    if (!name) return;
    if (!state.session) {
      state.authMessage = 'Log in to create leaderboards.';
      renderApp();
      return;
    }
    alert('Leaderboards are created automatically the first time a player submits a score for a new leaderboard ID via the client API.');
  });
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
  state.selectedGameId = game.game_id;
  state.selectedLeaderboardId = leaderboard.leaderboard_id;
  saveUiState();

  if (!state.leaderboardData && !state.loading) {
    openLeaderboard(game.game_id, leaderboard.leaderboard_id, state.page);
    return;
  }

  const pageSize = 100;
  const leaderboardData = state.leaderboardData;
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
