export const STATUSES = ['pending', 'needs_clarification', 'completed', 'escalated'];
export const PRIORITIES = ['low', 'normal', 'high', 'urgent'];

export const STATUS_META = {
  pending: { label: 'Pending', cls: 'bg-blue-100 text-blue-800 dark:bg-blue-500/20 dark:text-blue-300' },
  needs_clarification: { label: 'Needs info', cls: 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300' },
  completed: { label: 'Completed', cls: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300' },
  escalated: { label: 'Escalated', cls: 'bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300' },
};

export const PRIORITY_META = {
  low: 'text-slate-500 dark:text-slate-400',
  normal: 'text-slate-700 dark:text-slate-300',
  high: 'text-amber-700 dark:text-amber-400',
  urgent: 'text-red-700 dark:text-red-400',
};

export const OUTCOME_LABELS = {
  ask_for_clarification: 'Ask for clarification',
  ready_for_review: 'Ready for review',
  needs_human_review: 'Needs human review',
};

export const KIND_LABELS = {
  created: 'Created',
  status_change: 'Status change',
  advisory_analysis: 'Advisory analysis',
};

export function formatDate(iso) {
  if (!iso) return '-';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

export const cardCls = 'rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900';
export const inputCls =
  'w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 dark:border-slate-700 dark:bg-slate-900';
export const btnPrimary =
  'inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60';
export const btnGhost =
  'inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:hover:bg-slate-800';
export const btnDanger =
  'inline-flex items-center justify-center gap-2 rounded-lg border border-red-300 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-60 dark:border-red-500/40 dark:text-red-400 dark:hover:bg-red-500/10';
