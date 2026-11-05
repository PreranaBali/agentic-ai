import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { api } from '../../services/api.js';
import { PRIORITIES, btnGhost, btnPrimary, inputCls } from '../../utils/format.js';

const EMPTY = {
  requester_name: '',
  equipment: '',
  part_description: '',
  part_number: '',
  quantity: 1,
  priority: 'normal',
  notes: '',
};

function validate(v) {
  const errors = {};
  if (!v.requester_name.trim()) errors.requester_name = 'Enter the requester name.';
  if (v.part_description.trim().length < 3) errors.part_description = 'Describe the part (at least 3 characters).';
  const q = Number(v.quantity);
  if (!Number.isInteger(q) || q < 1 || q > 1000) errors.quantity = 'Quantity must be a whole number from 1 to 1000.';
  return errors;
}

function Field({ label, error, children }) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block font-medium">{label}</span>
      {children}
      {error && <span className="mt-1 block text-xs text-red-600 dark:text-red-400">{error}</span>}
    </label>
  );
}

export default function RequestForm({ onCreated, onCancel }) {
  const [values, setValues] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState('');
  const [busy, setBusy] = useState(false);

  const set = (key) => (e) => setValues((v) => ({ ...v, [key]: e.target.value }));

  async function submit(e) {
    e.preventDefault();
    const found = validate(values);
    setErrors(found);
    if (Object.keys(found).length) return;
    setBusy(true);
    setSubmitError('');
    try {
      const created = await api.createRequest({ ...values, quantity: Number(values.quantity) });
      onCreated(created);
    } catch (err) {
      setSubmitError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-3" noValidate>
      <Field label="Requester name *" error={errors.requester_name}>
        <input className={inputCls} value={values.requester_name} onChange={set('requester_name')} placeholder="Sam Rivera" />
      </Field>
      <Field label="Equipment (vehicle or machine)">
        <input className={inputCls} value={values.equipment} onChange={set('equipment')} placeholder="Forklift F-12" />
      </Field>
      <Field label="Part description *" error={errors.part_description}>
        <input className={inputCls} value={values.part_description} onChange={set('part_description')} placeholder="Front left brake pad" />
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Part number">
          <input className={inputCls} value={values.part_number} onChange={set('part_number')} placeholder="BP-1001" />
        </Field>
        <Field label="Quantity" error={errors.quantity}>
          <input className={inputCls} type="number" min="1" max="1000" value={values.quantity} onChange={set('quantity')} />
        </Field>
      </div>
      <Field label="Priority">
        <select className={inputCls} value={values.priority} onChange={set('priority')}>
          {PRIORITIES.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </Field>
      <Field label="Notes">
        <textarea className={inputCls} rows={3} value={values.notes} onChange={set('notes')} />
      </Field>
      {submitError && <div className="text-sm text-red-600 dark:text-red-400">{submitError}</div>}
      <div className="flex justify-end gap-2 pt-1">
        <button type="button" className={btnGhost} onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className={btnPrimary} disabled={busy}>
          {busy && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
          Create request
        </button>
      </div>
    </form>
  );
}
