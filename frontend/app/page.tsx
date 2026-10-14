'use client';

import { useMemo, useState } from 'react';

type FormState = {
  request_text: string;
  order_id: string;
  user_id: string;
  user_roles: string;
  user_permissions: string;
  approval_decision?: string;
  approval_status?: string;
  approved_by?: string;
};

const initialForm: FormState = {
  request_text: 'Check ORD-2001 order exception',
  order_id: 'ORD-2001',
  user_id: 'ops-analyst',
  user_roles: 'fulfillment_ops',
  user_permissions: 'read:orders,read:inventory,read:policies',
  approval_decision: 'APPROVED',
  approval_status: 'APPROVED',
  approved_by: 'ops-manager',
};

const queue = [
  { orderId: 'ORD-2001', issue: 'Inventory shortage', priority: 'High', status: 'Awaiting approval', owner: 'ops-analyst' },
  { orderId: 'ORD-2002', issue: 'Payment failure', priority: 'Medium', status: 'Manual review', owner: 'financeops' },
  { orderId: 'ORD-2003', issue: 'Address validation', priority: 'Medium', status: 'Pending customer confirmation', owner: 'ops-manager' },
];

export default function HomePage() {
  const [form, setForm] = useState<FormState>(initialForm);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<string>(queue[0].orderId);

  const selectedCase = useMemo(
    () => queue.find((item) => item.orderId === selectedOrder) ?? queue[0],
    [selectedOrder],
  );

  const updateField = (field: keyof FormState, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const submit = async (route: 'investigate' | 'approve') => {
    setLoading(true);
    setError('');

    try {
      const payload = {
        request_text: form.request_text,
        order_id: form.order_id,
        user_id: form.user_id,
        user_roles: form.user_roles.split(',').map((value) => value.trim()).filter(Boolean),
        user_permissions: form.user_permissions.split(',').map((value) => value.trim()).filter(Boolean),
        approval_decision: form.approval_decision || undefined,
        approval_status: form.approval_status || undefined,
        approved_by: form.approved_by || undefined,
      };

      const response = await fetch(`http://localhost:8000/api/v1/exception/${route}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || 'Request failed.');
      }

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page-shell">
      <div className="panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operations command center</p>
            <h1>Fulfillment Exception Dashboard</h1>
          </div>
          <div className="status-pill">System healthy</div>
        </header>

        <section className="stats-grid">
          <article className="stat-card">
            <span>Open cases</span>
            <strong>18</strong>
          </article>
          <article className="stat-card">
            <span>Needs approval</span>
            <strong>05</strong>
          </article>
          <article className="stat-card">
            <span>Auto-resolved</span>
            <strong>12</strong>
          </article>
          <article className="stat-card">
            <span>Avg SLA</span>
            <strong>2.4h</strong>
          </article>
        </section>

        <section className="content-grid">
          <div className="case-panel">
            <div className="section-head">
              <h2>Case queue</h2>
            </div>
            <div className="case-list">
              {queue.map((item) => (
                <button
                  key={item.orderId}
                  type="button"
                  className={`case-item ${selectedOrder === item.orderId ? 'active' : ''}`}
                  onClick={() => setSelectedOrder(item.orderId)}
                >
                  <div className="case-row">
                    <strong>{item.orderId}</strong>
                    <span className={`priority ${item.priority.toLowerCase()}`}>{item.priority}</span>
                  </div>
                  <div className="case-meta">{item.issue}</div>
                  <div className="case-foot">
                    <span>{item.status}</span>
                    <span>{item.owner}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <aside className="summary-panel">
            <div className="section-head">
              <h2>Selected case</h2>
            </div>
            <div className="summary-card">
              <div className="summary-header">
                <strong>{selectedCase.orderId}</strong>
                <span className={`priority ${selectedCase.priority.toLowerCase()}`}>{selectedCase.priority}</span>
              </div>
              <p>{selectedCase.issue}</p>
              <ul>
                <li>Owner: {selectedCase.owner}</li>
                <li>Status: {selectedCase.status}</li>
                <li>Recommended action: Alternate warehouse fulfillment</li>
              </ul>
            </div>
          </aside>
        </section>

        <section className="workflow-panel">
          <div className="section-head">
            <h2>Exception workflow</h2>
          </div>

          <div className="form-grid">
            <label>
              Request text
              <textarea value={form.request_text} onChange={(event) => updateField('request_text', event.target.value)} rows={3} />
            </label>

            <label>
              Order ID
              <input value={form.order_id} onChange={(event) => updateField('order_id', event.target.value)} />
            </label>

            <label>
              User ID
              <input value={form.user_id} onChange={(event) => updateField('user_id', event.target.value)} />
            </label>

            <label>
              User roles
              <input value={form.user_roles} onChange={(event) => updateField('user_roles', event.target.value)} />
            </label>

            <label>
              Permissions
              <input value={form.user_permissions} onChange={(event) => updateField('user_permissions', event.target.value)} />
            </label>

            <label>
              Approval decision
              <input value={form.approval_decision || ''} onChange={(event) => updateField('approval_decision', event.target.value)} />
            </label>

            <label>
              Approval status
              <input value={form.approval_status || ''} onChange={(event) => updateField('approval_status', event.target.value)} />
            </label>

            <label>
              Approved by
              <input value={form.approved_by || ''} onChange={(event) => updateField('approved_by', event.target.value)} />
            </label>
          </div>

          <div className="actions">
            <button type="button" onClick={() => submit('investigate')} disabled={loading}>
              {loading ? 'Running...' : 'Investigate'}
            </button>
            <button type="button" className="secondary" onClick={() => submit('approve')} disabled={loading}>
              Approve action
            </button>
          </div>

          {error ? <div className="error-box">{error}</div> : null}

          {result ? (
            <section className="result-box">
              <h2>Workflow result</h2>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </section>
          ) : null}
        </section>
      </div>
    </main>
  );
}
