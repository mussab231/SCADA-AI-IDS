import { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { io } from 'socket.io-client';
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ReferenceLine, ResponsiveContainer, CartesianGrid,
} from 'recharts';

// ─── Constants ────────────────────────────────────────────────────────────────
const API = 'http://localhost:5000';
const MAX_CHART_POINTS = 80;

const C = {
  bg:        '#0a0e1a',
  surface:   '#111827',
  border:    '#1e2d40',
  textPrim:  '#e2e8f0',
  textMuted: '#64748b',
  cyan:      '#06b6d4',
  green:     '#10b981',
  red:       '#ef4444',
  amber:     '#f59e0b',
  water:     '#2563eb',
  waterHigh: '#ef4444',
};

// ─── Extracted Components (DO NOT NEST THESE) ─────────────────────────────────
function Tank({ x, y, w, h, level, color, label, value }) {
  const fillH = Math.max(h * level, 2);
  const fillY = y + h - fillH;
  return (
    <g>
      <rect x={x} y={y} width={w} height={h} rx="4" fill="#0d1b2e" stroke={C.border} strokeWidth="1.5" />
      <rect x={x+1} y={fillY} width={w-2} height={fillH} rx="2" fill={color} opacity="0.75" />
      <text x={x + w/2} y={y + h/2 - 4} textAnchor="middle" fill={C.textPrim} fontSize="11" fontFamily="'Courier New', monospace" fontWeight="600">
        {(level * 100).toFixed(0)}%
      </text>
      <text x={x + w/2} y={y + h/2 + 10} textAnchor="middle" fill={C.textMuted} fontSize="9" fontFamily="'Courier New', monospace">
        {value}
      </text>
      <text x={x + w/2} y={y + h + 14} textAnchor="middle" fill={C.textMuted} fontSize="9" fontFamily="'Courier New', monospace" letterSpacing="0.5">
        {label}
      </text>
    </g>
  );
}

function Valve({ x, y, open, label }) {
  const color = open ? C.green : '#374151';
  return (
    <g>
      <circle cx={x} cy={y} r={7} fill={color} opacity="0.9" />
      <circle cx={x} cy={y} r={7} fill="none" stroke="#1e2d40" strokeWidth="1" />
      {label && (
        <text x={x + 10} y={y + 4} fill={C.textMuted} fontSize="8" fontFamily="'Courier New', monospace">{label}</text>
      )}
    </g>
  );
}

// ─── Plant Schematic SVG Component ───────────────────────────────────────────
function PlantSchematic({ data, isAttack }) {
  const { tank0 = 0, tank1 = 0, tank2 = 0,
          fillValve0 = 0, dischValve0 = 0,
          fillValve1 = 0, dischValve1 = 0,
          fillValve2 = 0, dischValve2 = 0 } = data;

  const lvl0 = Math.min(Math.max(tank0 / 1000, 0), 1);
  const lvl1 = Math.min(Math.max(tank1 / 1000, 0), 1);
  const lvl2 = Math.min(Math.max(tank2 / 1000, 0), 1);

  const fv0Open  = fillValve0  > 500;
  const dv0Open  = dischValve0 > 500;
  const fv1Open  = fillValve1  > 500;
  const dv1Open  = dischValve1 > 500;
  const fv2Open  = fillValve2  > 500;
  const dv2Open  = dischValve2 > 500;

  const col0 = isAttack ? C.waterHigh : C.water;
  const col1 = C.water;
  const col2 = C.water;

  const T0 = { x: 210, y: 10, w: 140, h: 90 };
  const T1 = { x: 40,  y: 170, w: 130, h: 85 };
  const T2 = { x: 390, y: 170, w: 130, h: 85 };
  const cx0 = T0.x + T0.w / 2;
  const cx1 = T1.x + T1.w / 2;
  const cx2 = T2.x + T2.w / 2;

  return (
    <svg viewBox="0 0 560 280" style={{ width: '100%', height: 'auto' }} role="img" aria-label="Plant schematic showing three tanks and valve states">
      <line x1={cx0} y1={0} x2={cx0} y2={T0.y} stroke={fv0Open ? C.cyan : C.border} strokeWidth="3" />
      <Valve x={cx0} y={5} open={fv0Open} />

      <Tank x={T0.x} y={T0.y} w={T0.w} h={T0.h} level={lvl0} color={col0} label="TANK 0 — MAIN" value={`${tank0} / 1000`} />

      <line x1={cx0} y1={T0.y + T0.h} x2={cx0} y2={150} stroke={dv0Open ? C.cyan : C.border} strokeWidth="3" />
      <Valve x={cx0} y={T0.y + T0.h + 10} open={dv0Open} />

      <line x1={cx1} y1={150} x2={cx2} y2={150} stroke={C.border} strokeWidth="3" />

      <line x1={cx1} y1={150} x2={cx1} y2={T1.y} stroke={fv1Open ? C.cyan : C.border} strokeWidth="3" />
      <Valve x={cx1} y={158} open={fv1Open} />

      <line x1={cx2} y1={150} x2={cx2} y2={T2.y} stroke={fv2Open ? C.cyan : C.border} strokeWidth="3" />
      <Valve x={cx2} y={158} open={fv2Open} />

      <Tank x={T1.x} y={T1.y} w={T1.w} h={T1.h} level={lvl1} color={col1} label="TANK 1" value={`${tank1} / 1000`} />
      <Tank x={T2.x} y={T2.y} w={T2.w} h={T2.h} level={lvl2} color={col2} label="TANK 2" value={`${tank2} / 1000`} />

      <line x1={cx1} y1={T1.y + T1.h} x2={cx1} y2={270} stroke={dv1Open ? C.cyan : C.border} strokeWidth="3" />
      <Valve x={cx1} y={T1.y + T1.h + 8} open={dv1Open} />

      <line x1={cx2} y1={T2.y + T2.h} x2={cx2} y2={270} stroke={dv2Open ? C.cyan : C.border} strokeWidth="3" />
      <Valve x={cx2} y={T2.y + T2.h + 8} open={dv2Open} />

      <g transform="translate(200, 240)">
        <circle cx={0} cy={0} r={5} fill={C.green} />
        <text x={8} y={4} fill={C.textMuted} fontSize="8" fontFamily="'Courier New', monospace">Valve open</text>
        <circle cx={70} cy={0} r={5} fill="#374151" />
        <text x={78} y={4} fill={C.textMuted} fontSize="8" fontFamily="'Courier New', monospace">Valve closed</text>
      </g>
    </svg>
  );
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#0d1b2e', border: `1px solid ${C.border}`, borderRadius: 6, padding: '6px 10px', fontFamily: "'Courier New', monospace" }}>
      <p style={{ color: C.textMuted, fontSize: 10, margin: 0 }}>{label}</p>
      <p style={{ color: C.cyan, fontSize: 12, margin: '2px 0 0' }}>MSE: {payload[0].value?.toFixed(5)}</p>
    </div>
  );
}

// ─── Main Dashboard ───────────────────────────────────────────────────────────
export default function Dashboard() {
  const navigate = useNavigate();
  const socketRef = useRef(null);

  const [connected, setConnected]   = useState(false);
  const [systemData, setSystemData] = useState({
    status: 'WAITING', tank0: 0, tank1: 0, tank2: 0,
    mixRatio: 0, tank0_error: 0, threshold: 0.048,
    attackType: null, attackId: null, isAttack: false,
    fillValve0: 0, dischValve0: 0,
    fillValve1: 0, dischValve1: 0,
    fillValve2: 0, dischValve2: 0,
  });
  const [mseHistory, setMseHistory] = useState([]);
  const [incidents,  setIncidents]  = useState([]);
  const [loadingInc, setLoadingInc] = useState(true);

  const token = localStorage.getItem('scada_token');

  useEffect(() => {
    if (!token) navigate('/');
  }, [token, navigate]);

  // تعریف fetchIncidents أولاً قبل استخدامها في הـ useEffect القادم
  const fetchIncidents = useCallback(() => {
    fetch(`${API}/api/incidents`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) setIncidents(data);
        setLoadingInc(false);
      })
      .catch(() => setLoadingInc(false));
  }, [token]);

  // إعداد Socket.io
  useEffect(() => {
    const socket = io(API, { transports: ['websocket'] });
    socketRef.current = socket;

    socket.on('connect', () => setConnected(true));
    socket.on('disconnect', () => setConnected(false));

    socket.on('scada_update', data => {
      setSystemData(prev => ({
        ...prev,
        ...data,
        isAttack: data.status !== 'NORMAL' && data.status !== 'WAITING',
      }));

      setMseHistory(prev => {
        const now = new Date();
        const label = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
        const entry = { time: label, error: data.tank0_error ?? 0 };
        const updated = [...prev, entry];
        return updated.length > MAX_CHART_POINTS
          ? updated.slice(updated.length - MAX_CHART_POINTS)
          : updated;
      });

      if (data.status && data.status !== 'NORMAL') {
        fetchIncidents();
      }
    });

    return () => socket.disconnect();
  }, [fetchIncidents]); // تمت إضافة fetchIncidents إلى مصفوفة الاعتماديات

  useEffect(() => { fetchIncidents(); }, [fetchIncidents]);

  const handleLogout = () => {
    localStorage.removeItem('scada_token');
    navigate('/');
  };

  // إزالة status لأنها غير مستخدمة
  const { isAttack, attackType, attackId, tank0_error, threshold, mixRatio } = systemData;

  const pct0  = ((systemData.tank0 / 1000) * 100).toFixed(1);
  const mseDisplay = (tank0_error ?? 0).toFixed(5);
  const thrDisplay = (threshold  ?? 0).toFixed(5);

  return (
    <div style={{ background: C.bg, minHeight: '100vh', color: C.textPrim, fontFamily: "'Courier New', monospace" }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 20px', borderBottom: `1px solid ${C.border}`, background: C.surface }}>
        <div>
          <span style={{ color: C.cyan, fontWeight: 700, letterSpacing: 2, fontSize: 13 }}>SCADA IDS COMMAND CENTER</span>
          <span style={{ color: C.textMuted, fontSize: 10, marginLeft: 16 }}>Industrial Control System — Real-Time Monitoring</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{ fontSize: 11, color: connected ? C.green : C.amber, display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: connected ? C.green : C.amber, display: 'inline-block' }} />
            {connected ? 'BACKEND LIVE' : 'RECONNECTING...'}
          </span>
          <button onClick={handleLogout} style={{ background: 'transparent', border: `1px solid ${C.red}`, color: C.red, padding: '4px 12px', borderRadius: 4, cursor: 'pointer', fontSize: 10, letterSpacing: 1 }}>LOGOUT</button>
        </div>
      </header>

      <div style={{ margin: '12px 16px', background: isAttack ? 'rgba(239,68,68,0.12)' : 'rgba(16,185,129,0.08)', border: `1px solid ${isAttack ? C.red : C.green}`, borderRadius: 6, padding: '10px 18px', display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 18 }}>{isAttack ? '⚠' : '✔'}</span>
        <div>
          <span style={{ fontWeight: 700, letterSpacing: 2, fontSize: 13, color: isAttack ? C.red : C.green }}>{isAttack ? 'CYBER ATTACK DETECTED' : 'SYSTEM SECURE'}</span>
          <span style={{ color: C.textMuted, fontSize: 11, marginLeft: 16 }}>
            {isAttack ? `[ATTACK-${attackId} | ${attackType}]  MSE ${mseDisplay} > ${thrDisplay}  |  TANK 0 = ${systemData.tank0}` : `[NORMAL]  MSE ${mseDisplay}  |  Tank0=${systemData.tank0}  MixRatio=${mixRatio}`}
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 260px', gap: 12, margin: '0 16px 12px' }}>
        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 6, padding: '10px 14px' }}>
          <div style={{ color: C.textMuted, fontSize: 10, letterSpacing: 1, marginBottom: 8 }}>PLANT SCHEMATIC — LIVE</div>
          <PlantSchematic data={systemData} isAttack={isAttack} />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {[
            { label: 'TANK 0 ERROR (MSE)', val: mseDisplay, color: isAttack ? C.red : C.green },
            { label: 'THRESHOLD',          val: thrDisplay, color: C.textMuted },
            { label: 'TANK 0 LEVEL',       val: `${pct0}%  (${systemData.tank0})`, color: C.cyan },
            { label: 'TANK 1 LEVEL',       val: `${((systemData.tank1/1000)*100).toFixed(1)}%  (${systemData.tank1})`, color: C.cyan },
            { label: 'TANK 2 LEVEL',       val: `${((systemData.tank2/1000)*100).toFixed(1)}%  (${systemData.tank2})`, color: C.cyan },
            { label: 'MIX RATIO',          val: systemData.mixRatio, color: C.textMuted },
            { label: 'INCIDENTS (TOTAL)',   val: incidents.length,    color: incidents.length > 0 ? C.amber : C.green },
          ].map(({ label, val, color }) => (
            <div key={label} style={{ background: '#0d1b2e', border: `1px solid ${C.border}`, borderRadius: 4, padding: '7px 12px' }}>
              <div style={{ color: C.textMuted, fontSize: 9, letterSpacing: 0.5 }}>{label}</div>
              <div style={{ color, fontSize: 13, fontWeight: 700, marginTop: 2 }}>{val}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 6, margin: '0 16px 12px', padding: '10px 14px' }}>
        <div style={{ color: C.textMuted, fontSize: 10, letterSpacing: 1, marginBottom: 8 }}>LIVE ANOMALY DETECTION — MSE STREAM</div>
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={mseHistory} margin={{ top: 4, right: 10, left: -10, bottom: 4 }}>
            <CartesianGrid stroke="#1e2d40" strokeDasharray="3 3" />
            <XAxis dataKey="time" tick={{ fill: C.textMuted, fontSize: 9, fontFamily: "'Courier New', monospace" }} interval="preserveStartEnd" tickLine={false} />
            <YAxis tick={{ fill: C.textMuted, fontSize: 9, fontFamily: "'Courier New', monospace" }} tickLine={false} axisLine={false} tickFormatter={v => v.toFixed(3)} />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={threshold} stroke={C.amber} strokeDasharray="5 3" label={{ value: 'THRESHOLD', fill: C.amber, fontSize: 9, position: 'insideTopRight' }} />
            <Line type="monotone" dataKey="error" stroke={isAttack ? C.red : C.cyan} strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 6, margin: '0 16px 16px', padding: '10px 14px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <span style={{ color: C.textMuted, fontSize: 10, letterSpacing: 1 }}>INCIDENT LOG — MONGODB ATLAS ({incidents.length} records)</span>
          <button onClick={fetchIncidents} style={{ background: 'transparent', border: `1px solid ${C.border}`, color: C.textMuted, padding: '2px 10px', borderRadius: 4, cursor: 'pointer', fontSize: 9, letterSpacing: 1 }}>REFRESH</button>
        </div>

        {loadingInc ? (
          <div style={{ color: C.textMuted, fontSize: 11, padding: '8px 0' }}>Loading incidents...</div>
        ) : incidents.length === 0 ? (
          <div style={{ color: C.green, fontSize: 11, padding: '8px 0' }}>No incidents recorded — system has been operating normally.</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 10 }}>
              <thead>
                <tr style={{ borderBottom: `1px solid ${C.border}` }}>
                  {['TIMESTAMP', 'STATUS', 'TYPE', 'TANK 0', 'MSE ERROR', 'THRESHOLD'].map(h => (
                    <th key={h} style={{ padding: '4px 10px', color: C.textMuted, fontWeight: 400, textAlign: 'left', letterSpacing: 0.5 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {incidents.map((inc, i) => (
                  <tr key={inc._id || i} style={{ borderBottom: `1px solid ${C.border}`, background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)' }}>
                    <td style={{ padding: '5px 10px', color: C.textMuted }}>{new Date(inc.timestamp).toLocaleString()}</td>
                    <td style={{ padding: '5px 10px', color: C.red, fontWeight: 700 }}>{inc.status}</td>
                    <td style={{ padding: '5px 10px', color: C.amber }}>{inc.attackType || '—'}</td>
                    <td style={{ padding: '5px 10px', color: C.textPrim }}>{inc.tank0 ?? '—'}</td>
                    <td style={{ padding: '5px 10px', color: C.red }}>{inc.tank0_error?.toFixed(5) ?? '—'}</td>
                    <td style={{ padding: '5px 10px', color: C.textMuted }}>{inc.threshold?.toFixed(5) ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}