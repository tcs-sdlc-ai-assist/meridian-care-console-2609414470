import { useState, type FormEvent } from 'react';

interface OutreachDialogProps {
  memberId: string;
  onClose: () => void;
  onSaved: () => Promise<void>;
}

export function OutreachDialog({ memberId, onClose, onSaved }: OutreachDialogProps): JSX.Element {
  const [channel, setChannel] = useState('phone');
  const [outcome, setOutcome] = useState('reached');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      const response = await fetch(`/api/v1/members/${memberId}/outreach`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('meridian-token')}` },
        body: JSON.stringify({ channel, outcome, notes }),
      });
      if (!response.ok) throw new Error('Unable to save outreach.');
      await onSaved();
      onClose();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to save outreach.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div role="dialog" aria-modal="true" aria-labelledby="log-outreach-title">
      <form className="card" onSubmit={submit}>
        <h2 id="log-outreach-title">Log outreach</h2>
        <label htmlFor="channel">Channel</label>
        <select id="channel" value={channel} onChange={(event) => setChannel(event.target.value)}>
          <option value="phone">phone</option>
          <option value="SMS">SMS</option>
          <option value="mail">mail</option>
          <option value="member portal">member portal</option>
        </select>
        <label htmlFor="outcome">Outcome</label>
        <select id="outcome" value={outcome} onChange={(event) => setOutcome(event.target.value)}>
          <option value="reached">reached</option>
          <option value="left message">left message</option>
          <option value="no answer">no answer</option>
          <option value="wrong number">wrong number</option>
        </select>
        <label htmlFor="outreach-notes">Notes</label>
        <textarea id="outreach-notes" value={notes} onChange={(event) => setNotes(event.target.value)} required minLength={1} />
        {error && <p role="alert" className="error">{error}</p>}
        <button className="button button-primary" disabled={saving}>{saving ? 'Saving…' : 'Save outreach'}</button>
        <button type="button" className="button button-secondary" onClick={onClose} disabled={saving}>Cancel</button>
      </form>
    </div>
  );
}
