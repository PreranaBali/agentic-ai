import { PriorityBadge, StatusBadge } from '../common/ui.jsx';
import { cardCls, formatDate } from '../../utils/format.js';

export default function RequestTable({ requests, selectedId, onSelect }) {
  return (
    <div className={`${cardCls} overflow-x-auto`}>
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead className="border-b border-slate-200 text-xs uppercase text-slate-500 dark:border-slate-800 dark:text-slate-400">
          <tr>
            <th className="px-4 py-3">ID</th>
            <th className="px-4 py-3">Part</th>
            <th className="px-4 py-3">Requester</th>
            <th className="px-4 py-3">Priority</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Created</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((r) => (
            <tr
              key={r.id}
              onClick={() => onSelect(r.id)}
              className={`cursor-pointer border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-800/60 dark:hover:bg-slate-800/50 ${
                selectedId === r.id ? 'bg-blue-50/60 dark:bg-blue-500/10' : ''
              }`}
            >
              <td className="px-4 py-3 text-slate-500">#{r.id}</td>
              <td className="px-4 py-3">
                <div className="font-medium">{r.part_description}</div>
                <div className="text-xs text-slate-500 dark:text-slate-400">{r.equipment || 'No equipment given'}</div>
              </td>
              <td className="px-4 py-3">{r.requester_name}</td>
              <td className="px-4 py-3">
                <PriorityBadge priority={r.priority} />
              </td>
              <td className="px-4 py-3">
                <StatusBadge status={r.status} />
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-slate-500 dark:text-slate-400">{formatDate(r.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
