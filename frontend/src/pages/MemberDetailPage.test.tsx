import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, expect, test, vi } from 'vitest';

import { AuthProvider } from '../auth/AuthProvider';
import MemberDetailPage from './MemberDetailPage';

const detail = {
  member_id: 'MEM-1001',
  name: 'Rosa Diaz',
  dob: '1958-04-12',
  plan: 'Meridian Gold',
  pcp: 'Dr. Patel',
  risk_level: 'high',
  coordinator_id: 'COORD-001',
  ssn: '***-**-6789',
  mbi: '****MK73',
  gaps: [{ gap_id: 'GAP-1001', type: 'A1c test overdue', status: 'open', closed_reason: null }],
  care_plan: [{ goal_id: 7, text: 'Complete diabetes self-management plan', status: 'not-started' }],
  outreach: [{ outreach_id: 'OUT-1001', coordinator_id: 'COORD-001', date: '2025-01-01T12:00:00Z', channel: 'phone', outcome: 'reached', notes: 'Member confirmed appointment.' }],
};

beforeEach(() => {
  localStorage.clear();
  localStorage.setItem('meridian-token', 'test-token');
  localStorage.setItem('meridian-user', JSON.stringify({ coordinator_id: 'COORD-001', name: 'Avery Chen', email: 'coordinator@meridian.example.com', role: 'coordinator' }));
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(detail) }));
});

test('renders masked identifiers, care plan, and newest outreach record', async () => {
  render(<AuthProvider><MemberDetailPage /></AuthProvider>);
  expect(await screen.findByText(/SSN \*\*\*-\*\*-6789/)).toBeVisible();
  expect(screen.getByText('Complete diabetes self-management plan')).toBeVisible();
  expect(screen.getByText(/Member confirmed appointment/)).toBeVisible();
});

test('updates a care-plan goal through the member workflow API', async () => {
  const fetchMock = vi.mocked(fetch);
  render(<AuthProvider><MemberDetailPage /></AuthProvider>);
  const status = await screen.findByLabelText('Goal status');
  fireEvent.change(status, { target: { value: 'met' } });
  expect(fetchMock).toHaveBeenCalledWith('/api/v1/members/MEM-1001/care-plan/7', expect.objectContaining({ method: 'PATCH', body: JSON.stringify({ status: 'met' }) }));
  expect(status).toHaveTextContent('met');
  expect(status).not.toHaveTextContent('completed');
});
