import { useCallback, useEffect, useState } from 'react';

import { useAuth } from '../auth/AuthProvider';
import { CareGapDialog } from '../components/CareGapDialog';
import { OutreachDialog } from '../components/OutreachDialog';

interface CareGap {
  gap_id: string;
  type: string;
  status: string;
  closed_reason: string | null;
}

interface CarePlanGoal {
  goal_id: number;
  text: string;
  status: 'not-started' | 'in-progress' | 'met';
}

interface Outreach {
  outreach_id: string;
  coordinator_id: string;
  date: string;
  channel: string;
  outcome: string;
  notes: string;
}

interface Detail {
  member_id: string;
  name: string;
  dob: string;
  plan: string;
  pcp: string;
  risk_level: string;
  coordinator_id: string;
  ssn: string;
  mbi: string;
  gaps: CareGap[];
  care_plan: CarePlanGoal[];
  outreach: Outreach[];
}

const memberId = 'MEM-1001';

export default function MemberDetailPage(): JSX.Element {
  const { user } = useAuth();
  const [detail, setDetail] = useState<Detail | null>(null);
  const [closing, setClosing] = useState('');
  const [outreach, setOutreach] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [savingGoal, setSavingGoal] = useState<number | null>(null);
  const [assignment, setAssignment] = useState('COORD-001');

  const loadDetail = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`/api/v1/members/${memberId}`, { headers: { Authorization: `Bearer ${localStorage.getItem('meridian-token')}` } });
      if (!response.ok) throw new Error('Unable to load member workflow details.');
      setDetail(await response.json() as Detail);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to load member workflow details.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void loadDetail(); }, [loadDetail]);

  async function updateGoal(goalId: number, status: CarePlanGoal['status']): Promise<void> {
    setSavingGoal(goalId);
    setError('');
    try {
      const response = await fetch(`/api/v1/members/${memberId}/care-plan/${goalId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('meridian-token')}` },
        body: JSON.stringify({ status }),
      });
      if (!response.ok) throw new Error('Unable to update goal status.');
      await loadDetail();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to update goal status.');
    } finally {
      setSavingGoal(null);
    }
  }

  async function assignMember(): Promise<void> {
    setError('');
    try {
      const response = await fetch(`/api/v1/members/${memberId}/assignment`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('meridian-token')}` },
        body: JSON.stringify({ coordinator_id: assignment }),
      });
      if (!response.ok) throw new Error('Unable to assign member.');
      await loadDetail();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to assign member.');
    }
  }

  if (loading) return <main className="page"><p>Loading member…</p></main>;
  if (!detail) return <main className="page"><p role="alert" className="error">{error || 'Member details are unavailable.'}</p><button className="button button-secondary" onClick={() => void loadDetail()}>Retry</button></main>;

  return (
    <main className="page">
      <h1>{detail.name}</h1>
      <p>{detail.dob} · {detail.plan} · {detail.pcp} · {detail.risk_level}</p>
      <p>SSN {detail.ssn} · MBI {detail.mbi}</p>
      {error && <p role="alert" className="error">{error}</p>}
      {user?.role === 'supervisor' && (
        <section className="card">
          <h2>Assignment</h2>
          <label htmlFor="assignment">Coordinator ID</label>
          <input id="assignment" value={assignment} onChange={(event) => setAssignment(event.target.value)} />
          <button className="button button-secondary" onClick={() => void assignMember()}>Assign member</button>
          <p>Current coordinator: {detail.coordinator_id}</p>
        </section>
      )}
      <section className="card">
        <h2>Care plan</h2>
        {detail.care_plan.length === 0 ? <p>No care-plan goals documented.</p> : detail.care_plan.map((goal) => (
          <div key={goal.goal_id}>
            <p>{goal.text}</p>
            <label htmlFor={`goal-${goal.goal_id}`}>Goal status</label>
            <select id={`goal-${goal.goal_id}`} value={goal.status} onChange={(event) => void updateGoal(goal.goal_id, event.target.value as CarePlanGoal['status'])} disabled={savingGoal === goal.goal_id || user?.role === 'auditor'}>
              <option value="not-started">not-started</option>
              <option value="in-progress">in-progress</option>
              <option value="met">met</option>
            </select>
          </div>
        ))}
      </section>
      <section className="card">
        <h2>Care gaps</h2>
        {detail.gaps.map((gap) => (
          <div key={gap.gap_id}>
            <p>{gap.type} — {gap.status}{gap.closed_reason ? ` (${gap.closed_reason})` : ''}</p>
            {gap.status === 'open' && user?.role !== 'auditor' && <button className="button button-secondary" onClick={() => setClosing(gap.gap_id)}>Close</button>}
          </div>
        ))}
      </section>
      <section className="card">
        <h2>Outreach history</h2>
        {detail.outreach.length === 0 ? <p>No outreach documented.</p> : detail.outreach.map((item) => <p key={item.outreach_id}>{new Date(item.date).toLocaleString()} · {item.channel} · {item.outcome} — {item.notes}</p>)}
      </section>
      {user?.role !== 'auditor' && <button className="button button-primary" onClick={() => setOutreach(true)}>Log outreach</button>}
      {closing && <CareGapDialog memberId={detail.member_id} gapId={closing} onClose={() => setClosing('')} onSaved={loadDetail} />}
      {outreach && <OutreachDialog memberId={detail.member_id} onClose={() => setOutreach(false)} onSaved={loadDetail} />}
    </main>
  );
}
