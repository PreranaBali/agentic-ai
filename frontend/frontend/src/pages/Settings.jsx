import { useState } from 'react';
import { Moon, Sun } from 'lucide-react';
import { api } from '../services/api.js';
import { useAsync } from '../hooks/useAsync.js';
import { useTheme } from '../context/ThemeContext.jsx';
import { useHealth } from '../hooks/useHealth.js';
import { ErrorBox, PageHeader, Spinner } from '../components/common/ui.jsx';
import { btnGhost, cardCls } from '../utils/format.js';

export default function Settings() {
  const { dark, toggle } = useTheme();
  const health = useHealth();
  const provider = useAsync(() => api.providerStatus());
  const [models, setModels] = useState(null);
  const [modelsError, setModelsError] = useState(null);
  const [loadingModels, setLoadingModels] = useState(false);

  async function loadModels() {
    setLoadingModels(true);
    setModelsError(null);
    try {
      setModels((await api.providerModels()).models);
    } catch (e) {
      setModelsError(e);
    } finally {
      setLoadingModels(false);
    }
  }

  const p = provider.data;

  return (
    <>
      <PageHeader title="Settings" subtitle="Connection details and appearance." />
      <div className="space-y-6">
        <section className={`${cardCls} space-y-2 p-4 text-sm`}>
          <h2 className="font-semibold">Backend</h2>
          <div className="flex justify-between">
            <span className="text-slate-500">API address</span>
            <code>{api.baseUrl}</code>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Status</span>
            <span className="capitalize">{health}</span>
          </div>
          <p className="text-xs text-slate-500">To change the address, set VITE_API_URL in frontend/.env and restart npm run dev.</p>
        </section>

        <section className={`${cardCls} space-y-2 p-4 text-sm`}>
          <h2 className="font-semibold">Groq</h2>
          {provider.loading && !p && <Spinner />}
          <ErrorBox error={provider.error} onRetry={provider.reload} />
          {p && (
            <>
              <div className="flex justify-between">
                <span className="text-slate-500">Model</span>
                <span>{p.model || 'Not set'}</span>
              </div>
              <p className="rounded-lg bg-slate-50 p-3 text-xs dark:bg-slate-800/60">{p.message}</p>
            </>
          )}
          <p className="text-xs text-slate-500">
            The API key and model are set in backend/.env. The key is never sent to or stored in the browser.
          </p>
          <button className={btnGhost} onClick={loadModels} disabled={loadingModels}>
            {loadingModels ? 'Loading...' : 'List available models'}
          </button>
          <ErrorBox error={modelsError} />
          {models && (
            <ul className="grid gap-1 text-xs sm:grid-cols-2">
              {models.map((m) => (
                <li key={m}>
                  <code>{m}</code>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className={`${cardCls} flex items-center justify-between p-4 text-sm`}>
          <h2 className="font-semibold">Theme</h2>
          <button className={btnGhost} onClick={toggle}>
            {dark ? <Sun className="h-4 w-4" aria-hidden="true" /> : <Moon className="h-4 w-4" aria-hidden="true" />}
            {dark ? 'Switch to light' : 'Switch to dark'}
          </button>
        </section>
      </div>
    </>
  );
}
