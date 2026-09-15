import { useState, type FormEvent } from 'react';

interface CareGapDialogProps {
  memberId: string;
  gapId: string;
  onClose: () => void;
  onSaved: () => Promise<void>;
}

export function CareGapDialog({ memberId, gapId, onClose, onSaved }: CareGapDialogProps): JSX.Element {
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      const response = await fetch(`/api/v1/members/${memberId}/gaps/${gapId}/close`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('meridian-token')}` },
        body: JSON.stringify({ reason }),
      });
      if (!response.ok) throw new Error('Unable to close this care gap.');
      await onSaved();
      onClose();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to close this care gap.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div role="dialog" aria-modal="true" aria-labelledby="close-care-gap-title">
      <form className="card" onSubmit={submit}>
        <h2 id="close-care-gap-title">Close care gap</h2>
        <label htmlFor="reason">Closure reason</label>
        <textarea id="reason" value={reason} onChange={(event) => setReason(event.target.value)} required minLength={2} />
        {error && <p role="alert" className="error">{error}</p>}
        <button className="button button-primary" disabled={saving}>{saving ? 'Saving…' : 'Save closure'}</button>
        <button type="button" className="button button-secondary" onClick={onClose} disabled={saving}>Cancel</button>
      </form>
    </div>
  );
}
