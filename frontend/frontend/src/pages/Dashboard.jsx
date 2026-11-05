import { Link, useNavigate } from 'react-router-dom';
import { AlertOctagon, CheckCircle2, Clock, HelpCircle, ListChecks, RefreshCw } from 'lucide-react';
import { api } from '../services/api.js';
import { useAsync } from '../hooks/useAsync.js';
import StatCard from '../components/dashboard/StatCard.jsx';
import RequestTable from '../components/requests/RequestTable.jsx';
import { EmptyState, ErrorBox, PageHeader, Spinner } from '../components/common/ui.jsx';
import { btnGhost, btnPrimary, cardCls, formatDate } from '../utils/format.js';

export default function Dashboard() {
  const navigate = useNavigate();
  const stats = useAsync(() => api.stats());
  const recent = useAsync(() => api.listRequests());
  const agent = useAsync(() => api.agentStatus());

  const reloadAll = () => {
    stats.reload();
    recent.reload();
    agent.reload();
  };
  const s = stats.data;
  const latest = (recent.data || []).slice(0, 5);

  return (
    <>
      <PageHeader title="Dashboard" subtitle="Live data from your backend.">
        <button className={btnGhost} onClick={reloadAll}>
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          Refresh
        </button>
      </PageHeader>

      <ErrorBox error={stats.error} onRetry={stats.reload} />

      <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
        <StatCard label="Total" value={s?.total} icon={ListChecks} />
        <StatCard label="Pending" value={s?.pending} icon={Clock} tone="text-blue-500" />
        <StatCard label="Needs info" value={s?.needs_clarification} icon={HelpCircle} tone="text-amber-500" />
        <StatCard label="Completed" value={s?.completed} icon={CheckCircle2} tone="text-emerald-500" />
        <StatCard label="Escalated" value={s?.escalated} icon={AlertOctagon} tone="text-red-500" />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <section className="lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-semibold">Recent requests</h2>
            <Link to="/requests" className="text-sm text-blue-600 hover:underline dark:text-blue-400">
              View all
            </Link>
          </div>
          {recent.loading && !recent.data && <Spinner />}
          <ErrorBox error={recent.error} onRetry={recent.reload} />
          {recent.data && latest.length === 0 && (
            <div className={cardCls}>
              <EmptyState
                title="No requests yet"
                text="Create your first parts request to see it here."
                action={
                  <Link to="/requests" className={`${btnPrimary} mt-2`}>
                    Go to requests
                  </Link>
                }
              />
            </div>
          )}
          {latest.length > 0 && (
            <RequestTable requests={latest} onSelect={(id) => navigate(`/requests?open=${id}`)} />
          )}
        </section>

        <section>
          <h2 className="mb-3 font-semibold">Agent activity</h2>
          <div className={`${cardCls} space-y-2 p-4 text-sm`}>
            {agent.loading && !agent.data && <Spinner />}
            <ErrorBox error={agent.error} onRetry={agent.reload} />
            {agent.data && (
              <>
                <div className="flex justify-between">
                  <span className="text-slate-500">Analyses run</span>
                  <span>{agent.data.advisory_runs}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Failures</span>
                  <span>{agent.data.advisory_failures}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Last run</span>
                  <span>{formatDate(agent.data.last_run_at)}</span>
                </div>
                <div className="rounded-lg bg-amber-50 p-3 text-xs text-amber-800 dark:bg-amber-500/10 dark:text-amber-300">
                  Competition agent: {agent.data.competition_agent.state}. {agent.data.competition_agent.message}
                </div>
              </>
            )}
          </div>
        </section>
      </div>
    </>
  );
}
