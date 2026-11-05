import { useEffect } from 'react';
import { CheckCircle2, RefreshCw, XCircle } from 'lucide-react';
import { api } from '../services/api.js';
import { useAsync } from '../hooks/useAsync.js';
import { EmptyState, ErrorBox, PageHeader, Spinner } from '../components/common/ui.jsx';
import { btnGhost, cardCls, formatDate } from '../utils/format.js';

export default function AgentMonitor() {
  const agent = useAsync(() => api.agentStatus());
  const provider = useAsync(() => api.providerStatus());

  useEffect(() => {
    const t = setInterval(agent.reload, 10000);
    return () => clearInterval(t);
  }, [agent.reload]);

  const d = agent.data;
  const p = provider.data;
  const refresh = () => {
    agent.reload();
    provider.reload();
  };

  return (
    <>
      <PageHeader title="Agent monitor" subtitle="Advisory assistant activity and Groq connection. Refreshes every 10 seconds.">
        <button className={btnGhost} onClick={refresh}>
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          Refresh
        </button>
      </PageHeader>

      <div className="grid gap-6 md:grid-cols-2">
        <section className={`${cardCls} space-y-2 p-4 text-sm`}>
          <h2 className="font-semibold">Groq connection</h2>
          {provider.loading && !p && <Spinner />}
          <ErrorBox error={provider.error} onRetry={provider.reload} />
          {p && (
            <>
              <div className="flex justify-between">
                <span className="text-slate-500">Configured</span>
                <span>{p.configured ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Reachable</span>
                <span>{p.reachable === null ? 'Not checked' : p.reachable ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Model</span>
                <span>{p.model || 'Not set'}</span>
              </div>
              <p className="rounded-lg bg-slate-50 p-3 text-xs dark:bg-slate-800/60">{p.message}</p>
            </>
          )}
        </section>

        <section className={`${cardCls} space-y-2 p-4 text-sm`}>
          <h2 className="font-semibold">Competition agent</h2>
          {d ? (
            <>
              <div className="flex justify-between">
                <span className="text-slate-500">State</span>
                <span className="font-medium capitalize">{d.competition_agent.state}</span>
              </div>
              <p className="rounded-lg bg-amber-50 p-3 text-xs text-amber-800 dark:bg-amber-500/10 dark:text-amber-300">
                {d.competition_agent.message}
              </p>
            </>
          ) : (
            <Spinner />
          )}
        </section>
      </div>

      <section className={`${cardCls} mt-6 p-4`}>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="font-semibold">Recent analysis runs</h2>
          {d && (
            <span className="text-xs text-slate-500">
              {d.advisory_runs} run(s), {d.advisory_failures} failure(s)
            </span>
          )}
        </div>
        <ErrorBox error={agent.error} onRetry={agent.reload} />
        {d && d.recent_events.length === 0 && (
          <EmptyState title="No analysis runs yet" text="Open a request and choose Run advisory analysis." />
        )}
        <ul className="divide-y divide-slate-100 text-sm dark:divide-slate-800">
          {(d?.recent_events || []).map((e, i) => (
            <li key={i} className="flex items-start gap-3 py-2.5">
              {e.ok ? (
                <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-500" aria-label="Succeeded" />
              ) : (
                <XCircle className="mt-0.5 h-4 w-4 text-red-500" aria-label="Failed" />
              )}
              <div className="flex-1">
                <div>
                  Request #{e.request_id} - {e.groq_used ? 'Groq + rules' : 'Rules only'}
                </div>
                <div className="text-xs text-slate-500">{e.detail}</div>
              </div>
              <span className="whitespace-nowrap text-xs text-slate-500">{formatDate(e.time)}</span>
            </li>
          ))}
        </ul>
      </section>
    </>
  );
}
