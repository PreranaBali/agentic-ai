import { useState } from 'react';
import { Link } from 'react-router-dom';
import { RefreshCw } from 'lucide-react';
import { api } from '../services/api.js';
import { useAsync } from '../hooks/useAsync.js';
import { EmptyState, ErrorBox, PageHeader, Spinner } from '../components/common/ui.jsx';
import { KIND_LABELS, btnGhost, cardCls, formatDate, inputCls } from '../utils/format.js';

export default function History() {
  const [kind, setKind] = useState('');
  const { data, error, loading, reload } = useAsync(() => api.decisions({ limit: 200 }));
  const rows = (data || []).filter((d) => !kind || d.kind === kind);

  return (
    <>
      <PageHeader title="Decision history" subtitle="Every creation, status change and analysis, newest first.">
        <select className={`${inputCls} !w-auto`} value={kind} onChange={(e) => setKind(e.target.value)} aria-label="Filter by type">
          <option value="">All types</option>
          {Object.entries(KIND_LABELS).map(([k, label]) => (
            <option key={k} value={k}>
              {label}
            </option>
          ))}
        </select>
        <button className={btnGhost} onClick={reload}>
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          Refresh
        </button>
      </PageHeader>

      {loading && !data && <Spinner />}
      <ErrorBox error={error} onRetry={reload} />

      {data && rows.length === 0 && (
        <div className={cardCls}>
          <EmptyState title="No history yet" text="Decisions appear here as requests are created and reviewed." />
        </div>
      )}
      {rows.length > 0 && (
        <ul className={`${cardCls} divide-y divide-slate-100 dark:divide-slate-800`}>
          {rows.map((d) => (
            <li key={d.id} className="flex flex-wrap items-start justify-between gap-2 px-4 py-3 text-sm">
              <div>
                <div className="font-medium">
                  {KIND_LABELS[d.kind] || d.kind}{' '}
                  <Link to={`/requests?open=${d.request_id}`} className="font-normal text-blue-600 hover:underline dark:text-blue-400">
                    request #{d.request_id}
                  </Link>
                </div>
                <div className="text-slate-600 dark:text-slate-300">{d.summary}</div>
                <div className="text-xs text-slate-500">Source: {d.source}</div>
              </div>
              <span className="whitespace-nowrap text-xs text-slate-500">{formatDate(d.created_at)}</span>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
