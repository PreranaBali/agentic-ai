import { cardCls } from '../../utils/format.js';

export default function StatCard({ label, value, icon: Icon, tone = 'text-slate-500' }) {
  return (
    <div className={`${cardCls} p-4`}>
      <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
        {label}
        <Icon className={`h-4 w-4 ${tone}`} aria-hidden="true" />
      </div>
      <div className="mt-2 text-3xl font-semibold">{value ?? '-'}</div>
    </div>
  );
}
