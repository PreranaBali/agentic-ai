import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';
import { api } from '../services/api.js';
import { useAsync } from '../hooks/useAsync.js';
import RequestForm from '../components/requests/RequestForm.jsx';
import RequestTable from '../components/requests/RequestTable.jsx';
import RequestDetail from '../components/requests/RequestDetail.jsx';
import { EmptyState, ErrorBox, Modal, PageHeader, Spinner } from '../components/common/ui.jsx';
import { STATUSES, STATUS_META, btnPrimary, cardCls, inputCls } from '../utils/format.js';

export default function Requests() {
  const [params, setParams] = useSearchParams();
  const [status, setStatus] = useState('');
  const [search, setSearch] = useState('');
  const [debounced, setDebounced] = useState('');
  const [showForm, setShowForm] = useState(false);
  const selectedId = Number(params.get('open')) || null;

  useEffect(() => {
    const t = setTimeout(() => setDebounced(search.trim()), 300);
    return () => clearTimeout(t);
  }, [search]);

  const { data, error, loading, reload } = useAsync(
    () => api.listRequests({ status, search: debounced }),
    [status, debounced]
  );

  const open = (id) => setParams(id ? { open: String(id) } : {});
  const filtered = Boolean(status || debounced);

  return (
    <>
      <PageHeader title="Requests" subtitle="Create, review and track parts requests.">
        <button className={btnPrimary} onClick={() => setShowForm(true)}>
          <Plus className="h-4 w-4" aria-hidden="true" />
          New request
        </button>
      </PageHeader>

      <div className="mb-4 flex flex-wrap gap-3">
        <div className="relative min-w-[220px] flex-1">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" aria-hidden="true" />
          <input
            className={`${inputCls} pl-9`}
            placeholder="Search part, requester, equipment, part number"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search requests"
          />
        </div>
        <select className={`${inputCls} !w-auto`} value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Filter by status">
          <option value="">All statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {STATUS_META[s].label}
            </option>
          ))}
        </select>
      </div>

      {loading && !data && <Spinner />}
      <ErrorBox error={error} onRetry={reload} />

      {data && data.length === 0 && (
        <div className={cardCls}>
          <EmptyState
            title={filtered ? 'No matching requests' : 'Start your first request'}
            text={filtered ? 'Try a different search or status filter.' : 'Create a parts request to see it listed here.'}
            action={
              !filtered && (
                <button className={`${btnPrimary} mt-2`} onClick={() => setShowForm(true)}>
                  New request
                </button>
              )
            }
          />
        </div>
      )}
      {data && data.length > 0 && <RequestTable requests={data} selectedId={selectedId} onSelect={open} />}

      {showForm && (
        <Modal title="New parts request" onClose={() => setShowForm(false)}>
          <RequestForm
            onCancel={() => setShowForm(false)}
            onCreated={(created) => {
              setShowForm(false);
              reload();
              open(created.id);
            }}
          />
        </Modal>
      )}

      {selectedId && <RequestDetail id={selectedId} onClose={() => open(null)} onChanged={reload} />}
    </>
  );
}
