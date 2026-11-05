import { useEffect, useState } from 'react';
import { Loader2, Sparkles, Trash2, X } from 'lucide-react';
import { api } from '../../services/api.js';
import { useAsync } from '../../hooks/useAsync.js';
import AnalysisCard from '../agent/AnalysisCard.jsx';
import { ErrorBox, PriorityBadge, Spinner, StatusBadge } from '../common/ui.jsx';
import { KIND_LABELS, STATUSES, STATUS_META, btnDanger, btnGhost, btnPrimary, formatDate, inputCls } from '../../utils/format.js';

function Row({ label, children }) {
  return (
    <div className="flex justify-between gap-4 py-1.5 text-sm">
      <span className="text-slate-500 dark:text-slate-400">{label}</span>
      <span className="text-right">{children || '-'}</span>
    </div>
  );
}

export default function RequestDetail({ id, onClose, onChanged }) {
  const { data, error, loading, reload } = useAsync(() => api.getRequest(id), [id]);
  const [statusValue, setStatusValue] = useState('pending');
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [actionError, setActionError] = useState('');
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    setAnalysis(null);
    setActionError('');
    setNote('');
  }, [id]);

  useEffect(() => {
    if (data) setStatusValue(data.request.status);
  }, [data]);

  async function saveStatus() {
    setBusy(true);
    setActionError('');
    try {
      await api.updateStatus(id, statusValue, note);
      setNote('');
      await reload();
      onChanged();
    } catch (e) {
      setActionError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function runAnalysis() {
    setAnalyzing(true);
    setActionError('');
    try {
      setAnalysis(await api.analyze(id));
      await reload();
      onChanged();
    } catch (e) {
      setActionError(e.message);
    } finally {
      setAnalyzing(false);
    }
  }

  async function remove() {
    if (!window.confirm(`Delete request #${id}? This can't be undone.`)) return;
    setBusy(true);
    try {
      await api.deleteRequest(id);
      onChanged();
      onClose();
    } catch (e) {
      setActionError(e.message);
      setBusy(false);
    }
  }

  const request = data?.request;
  const decisions = data?.decisions || [];
  const latestAnalysis = analysis || decisions.find((d) => d.kind === 'advisory_analysis')?.details;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40" onMouseDown={onClose}>
      <aside
        className="h-full w-full max-w-lg overflow-y-auto border-l border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Request #{id}</h2>
          <button onClick={onClose} className={`${btnGhost} !p-1.5`} aria-label="Close panel">
            <X className="h-4 w-4" />
          </button>
        </div>

        {loading && !data && <Spinner />}
        <ErrorBox error={error} onRetry={reload} />

        {request && (
          <div className="space-y-5">
            <div className="divide-y divide-slate-100 dark:divide-slate-800">
              <Row label="Part">{request.part_description}</Row>
              <Row label="Part number">{request.part_number}</Row>
              <Row label="Equipment">{request.equipment}</Row>
              <Row label="Quantity">{request.quantity}</Row>
              <Row label="Requester">{request.requester_name}</Row>
              <Row label="Priority">
                <PriorityBadge priority={request.priority} />
              </Row>
              <Row label="Status">
                <StatusBadge status={request.status} />
              </Row>
              <Row label="Notes">{request.notes}</Row>
              <Row label="Created">{formatDate(request.created_at)}</Row>
            </div>

            <div>
              <button className={btnPrimary} onClick={runAnalysis} disabled={analyzing}>
                {analyzing ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Sparkles className="h-4 w-4" aria-hidden="true" />}
                {analyzing ? 'Analyzing...' : 'Run advisory analysis'}
              </button>
            </div>

            <AnalysisCard analysis={latestAnalysis} />

            <div className="space-y-2 rounded-xl border border-slate-200 p-4 dark:border-slate-800">
              <div className="text-sm font-medium">Update status</div>
              <select className={inputCls} value={statusValue} onChange={(e) => setStatusValue(e.target.value)}>
                {STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {STATUS_META[s].label}
                  </option>
                ))}
              </select>
              <input className={inputCls} placeholder="Optional note" value={note} onChange={(e) => setNote(e.target.value)} maxLength={500} />
              <button className={btnGhost} onClick={saveStatus} disabled={busy || statusValue === request.status}>
                Save status
              </button>
            </div>

            {actionError && <div className="text-sm text-red-600 dark:text-red-400">{actionError}</div>}

            <div>
              <div className="mb-2 text-sm font-medium">Decision history</div>
              <ol className="space-y-2">
                {decisions.map((d) => (
                  <li key={d.id} className="rounded-lg bg-slate-50 p-3 text-sm dark:bg-slate-800/60">
                    <div className="flex justify-between gap-2 text-xs text-slate-500 dark:text-slate-400">
                      <span>
                        {KIND_LABELS[d.kind] || d.kind} - {d.source}
                      </span>
                      <span>{formatDate(d.created_at)}</span>
                    </div>
                    <div className="mt-1">{d.summary}</div>
                    {d.details?.note && <div className="mt-1 text-xs text-slate-500">Note: {d.details.note}</div>}
                  </li>
                ))}
              </ol>
            </div>

            <button className={btnDanger} onClick={remove} disabled={busy}>
              <Trash2 className="h-4 w-4" aria-hidden="true" />
              Delete request
            </button>
          </div>
        )}
      </aside>
    </div>
  );
}
