import { Sparkles } from 'lucide-react';
import { OUTCOME_LABELS } from '../../utils/format.js';

function Section({ title, items }) {
  if (!items?.length) return null;
  return (
    <div className="mt-3">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">{title}</div>
      <ul className="mt-1 list-disc space-y-0.5 pl-5 text-sm">
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function AnalysisCard({ analysis }) {
  if (!analysis) return null;
  return (
    <div className="rounded-xl border border-violet-200 bg-violet-50 p-4 dark:border-violet-500/30 dark:bg-violet-500/10">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-sm font-medium text-violet-800 dark:text-violet-300">
          <Sparkles className="h-4 w-4" aria-hidden="true" />
          Advisory analysis
        </div>
        <span className="text-xs text-slate-600 dark:text-slate-400">
          {analysis.groq_used ? `Groq + rules (${analysis.model})` : 'Rules only'}
        </span>
      </div>
      <p className="mt-2 text-sm">{analysis.summary}</p>
      <div className="mt-2 text-sm">
        Suggested outcome:{' '}
        <strong>{OUTCOME_LABELS[analysis.suggested_review_outcome] || analysis.suggested_review_outcome}</strong>
      </div>
      <Section title="Missing information" items={analysis.missing_information} />
      <Section title="Questions to ask" items={analysis.clarifying_questions} />
      <Section title="Risk flags" items={analysis.risk_flags} />
      <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">{analysis.disclaimer}</p>
    </div>
  );
}
