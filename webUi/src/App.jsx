import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, Users, ShoppingCart, Receipt, Wallet, 
  Layers, BarChart3, Settings, LogIn, UserPlus, LogOut, Plus, 
  Search, Upload, ArrowRight, Download, Check, AlertTriangle, ShieldCheck,
  ChevronLeft, ChevronRight, Store, Sun, Moon, Building2, Database, Package,
  TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, DollarSign,
  Activity, PieChart, CreditCard, Palette, Edit, Trash2, MapPin, Phone, Mail, Send
} from 'lucide-react';

const API_BASE = '/api';

const exportToCSV = (data, headers, mapping, filename) => {
  const csvRows = [];
  // Add headers
  csvRows.push(headers.join(','));
  
  // Add rows
  for (const row of data) {
    const values = mapping.map(key => {
      const val = row[key];
      const stringVal = val === null || val === undefined ? '' : String(val);
      return `"${stringVal.replace(/"/g, '""')}"`;
    });
    csvRows.push(values.join(','));
  }
  
  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Theme state
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');

  // Auth state
  const [isRegister, setIsRegister] = useState(false);
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authName, setAuthName] = useState('');
  const [authError, setAuthError] = useState('');

  // App Master States
  const [customers, setCustomers] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [items, setItems] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [bills, setBills] = useState([]);
  const [payments, setPayments] = useState([]);
  const [settings, setSettings] = useState({});
  const [dashboardStats, setDashboardStats] = useState(null);
  const [outlets, setOutlets] = useState([]);
  const [selectedOutletFilter, setSelectedOutletFilter] = useState('all');

  // Sync auth headers
  const getHeaders = () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  });

  useEffect(() => {
    localStorage.setItem('theme', theme);
    // Remove all theme classes
    document.body.classList.remove('light-theme', 'theme-ocean', 'theme-emerald', 'theme-rose', 'theme-slate');
    if (theme === 'light') {
      document.body.classList.add('light-theme');
    } else if (theme === 'ocean') {
      document.body.classList.add('theme-ocean');
    } else if (theme === 'emerald') {
      document.body.classList.add('theme-emerald');
    } else if (theme === 'rose') {
      document.body.classList.add('theme-rose');
    } else if (theme === 'slate') {
      document.body.classList.add('theme-slate');
    }
    // 'dark' is the default :root, no class needed
  }, [theme]);

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      fetchUserProfile();
      loadAllData();
    } else {
      localStorage.removeItem('token');
      setUser(null);
    }
  }, [token, selectedOutletFilter]);

  const fetchUserProfile = async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, { headers: getHeaders() });
      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
      } else {
        handleLogout();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadAllData = async () => {
    try {
      // Load settings
      const settingsRes = await fetch(`${API_BASE}/settings`, { headers: getHeaders() });
      if (settingsRes.ok) setSettings(await settingsRes.json());

      // Load Customers
      const custRes = await fetch(`${API_BASE}/customers`, { headers: getHeaders() });
      if (custRes.ok) setCustomers(await custRes.json());

      // Load Vendors
      const vendRes = await fetch(`${API_BASE}/vendors`, { headers: getHeaders() });
      if (vendRes.ok) setVendors(await vendRes.json());

      // Load Items
      const itemsRes = await fetch(`${API_BASE}/items`, { headers: getHeaders() });
      if (itemsRes.ok) setItems(await itemsRes.json());

      // Load Invoices
      const invRes = await fetch(`${API_BASE}/invoices`, { headers: getHeaders() });
      if (invRes.ok) setInvoices(await invRes.json());

      // Load Bills
      const billRes = await fetch(`${API_BASE}/bills`, { headers: getHeaders() });
      if (billRes.ok) setBills(await billRes.json());

      // Load Payments
      const payRes = await fetch(`${API_BASE}/payments`, { headers: getHeaders() });
      if (payRes.ok) setPayments(await payRes.json());

      // Load Dashboard Analytics
      const statsRes = await fetch(`${API_BASE}/reports/dashboard?outlet_id=${selectedOutletFilter}`, { headers: getHeaders() });
      if (statsRes.ok) setDashboardStats(await statsRes.json());

      // Load Outlets
      const outletsRes = await fetch(`${API_BASE}/outlets`, { headers: getHeaders() });
      if (outletsRes.ok) setOutlets(await outletsRes.json());
    } catch (err) {
      console.error('Error fetching data', err);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authEmail, password: authPassword })
      });
      const data = await res.json();
      if (res.ok) {
        setToken(data.token);
      } else {
        setAuthError(data.error || 'Login failed');
      }
    } catch (err) {
      setAuthError('Connection failed');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: authName, email: authEmail, password: authPassword })
      });
      const data = await res.json();
      if (res.ok) {
        setIsRegister(false);
        setAuthError('Registration successful. Please login.');
      } else {
        setAuthError(data.error || 'Registration failed');
      }
    } catch (err) {
      setAuthError('Connection failed');
    }
  };

  const handleLogout = () => {
    setToken('');
    setUser(null);
  };

  // Database configuration states
  const [showDbConfig, setShowDbConfig] = useState(false);
  const [dbType, setDbType] = useState('mysql');
  const [dbHost, setDbHost] = useState('localhost');
  const [dbPort, setDbPort] = useState(3306);
  const [dbUser, setDbUser] = useState('root');
  const [dbPassword, setDbPassword] = useState('admin@angel');
  const [dbName, setDbName] = useState('ledgerpro');
  const [dbConfigMsg, setDbConfigMsg] = useState('');

  const handleSaveDbConfig = async (e) => {
    e.preventDefault();
    setDbConfigMsg('');
    try {
      const res = await fetch(`${API_BASE}/settings/db-config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: dbType, host: dbHost, port: parseInt(dbPort), user: dbUser, password: dbPassword, database: dbName })
      });
      const data = await res.json();
      if (res.ok) {
        setDbConfigMsg(data.message);
        setTimeout(() => setShowDbConfig(false), 2000);
      } else {
        setDbConfigMsg('Error: ' + data.error);
      }
    } catch (err) {
      setDbConfigMsg('Connection failed: ' + err.message);
    }
  };

  if (!token) {
    return (
      <div className="login-container">
        {/* Left Side: Blue Branding Panel */}
        <div className="login-left">
          <div style={{ maxWidth: '320px' }}>
            <img src="/br31logo.png" alt="TSL SwiftBill ERP Logo" style={{ width: '150px', height: 'auto', marginBottom: '24px', borderRadius: '16px', boxShadow: '0 8px 24px rgba(0,0,0,0.3)' }} onError={(e) => { e.target.style.display = 'none'; }} />
            <h1 style={{ fontSize: '2.5rem', fontWeight: '800', color: '#ffffff', marginBottom: '12px', fontFamily: 'var(--font-family-display)' }}>TSL SwiftBill ERP</h1>
            <p style={{ color: '#bfdbfe', fontSize: '1.1rem', marginBottom: '40px' }}>Professional Accounting & Inventory</p>
            
            <div style={{ fontSize: '0.85rem', color: '#93c5fd', marginTop: '60px', lineHeight: '1.6' }}>
              <p>Developed for The Space Labs</p>
              <p>Updated by Angel (Mehul) Singh</p>
              <p>Powered by Br31Technologies</p>
              <p style={{ marginTop: '12px', opacity: 0.8 }}>Version 3.5.0</p>
            </div>
          </div>
        </div>

        {/* Right Side: Login Form */}
        <div className="login-right">
          <div style={{ width: '100%', maxWidth: '360px' }}>
            <div style={{ marginBottom: '32px' }}>
              <h2 style={{ fontSize: '2rem', color: 'var(--text-primary)', marginBottom: '8px' }}>Secure Login</h2>
              <p style={{ color: 'var(--text-secondary)' }}>Please identify yourself to continue.</p>
            </div>

            {authError && (
              <div style={{ background: 'var(--danger-bg)', color: 'var(--danger)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '12px', borderRadius: 'var(--border-radius-sm)', marginBottom: '20px', fontSize: '0.9rem' }}>
                {authError}
              </div>
            )}

            <form onSubmit={isRegister ? handleRegister : handleLogin}>
              {isRegister && (
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input className="form-control" type="text" value={authName} onChange={e => setAuthName(e.target.value)} required placeholder="Angel Singh" />
                </div>
              )}
              <div className="form-group">
                <label className="form-label">User ID</label>
                <input className="form-control" type="email" value={authEmail} onChange={e => setAuthEmail(e.target.value)} required placeholder="Email ID / Username" />
              </div>
              <div className="form-group" style={{ marginBottom: '24px' }}>
                <label className="form-label">Password</label>
                <input className="form-control" type="password" value={authPassword} onChange={e => setAuthPassword(e.target.value)} required placeholder="Password" />
              </div>
              
              <button className="btn btn-primary" type="submit" style={{ width: '100%', padding: '12px', backgroundColor: '#1e3a8a', backgroundImage: 'none' }}>
                {isRegister ? 'REGISTER' : 'LOGIN'}
              </button>
            </form>

            <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              {isRegister ? (
                <a href="#" onClick={() => setIsRegister(false)} style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>Login here</a>
              ) : (
                <a href="#" onClick={() => setIsRegister(true)} style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>Register account</a>
              )}
              
              <a href="#" onClick={(e) => { e.preventDefault(); setShowDbConfig(true); }} style={{ color: 'var(--text-secondary)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>
                ⚙️ Database Setup
              </a>
            </div>
          </div>

          {/* Database Setup Dialog Overlay */}
          {showDbConfig && (
            <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1100 }}>
              <div className="card" style={{ width: '100%', maxWidth: '440px', padding: '30px' }}>
                <h3 style={{ marginBottom: '8px' }}>Database Configuration</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '20px' }}>Select your database backend. SQLite is local, MySQL is network-based.</p>
                
                {dbConfigMsg && (
                  <div style={{ background: dbConfigMsg.includes('Error') ? 'var(--danger-bg)' : 'var(--success-bg)', color: dbConfigMsg.includes('Error') ? 'var(--danger)' : 'var(--success)', padding: '10px', borderRadius: '4px', marginBottom: '16px', fontSize: '0.85rem' }}>
                    {dbConfigMsg}
                  </div>
                )}

                <form onSubmit={handleSaveDbConfig}>
                  <div className="form-group">
                    <label className="form-label">Database Type:</label>
                    <select className="form-control" value={dbType} onChange={e => setDbType(e.target.value)}>
                      <option value="mysql">mysql</option>
                      <option value="sqlite">sqlite</option>
                    </select>
                  </div>

                  {dbType === 'mysql' && (
                    <>
                      <div className="form-group">
                        <label className="form-label">Host:</label>
                        <input className="form-control" type="text" value={dbHost} onChange={e => setDbHost(e.target.value)} required />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Port:</label>
                        <input className="form-control" type="number" value={dbPort} onChange={e => setDbPort(e.target.value)} required />
                      </div>
                      <div className="form-group">
                        <label className="form-label">User:</label>
                        <input className="form-control" type="text" value={dbUser} onChange={e => setDbUser(e.target.value)} required />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Password:</label>
                        <input className="form-control" type="password" value={dbPassword} onChange={e => setDbPassword(e.target.value)} />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Database Name:</label>
                        <input className="form-control" type="text" value={dbName} onChange={e => setDbName(e.target.value)} required />
                      </div>
                    </>
                  )}

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
                    <button type="button" onClick={() => setShowDbConfig(false)} className="btn btn-secondary">Close</button>
                    <button type="submit" className="btn btn-primary" style={{ backgroundColor: '#1e3a8a', backgroundImage: 'none' }}>Save Settings</button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-primary)' }}>
      {/* Sidebar Navigation */}
      <div style={{ 
        width: sidebarCollapsed ? '80px' : '260px', 
        transition: 'width 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
        background: 'rgba(30, 41, 59, 0.55)', 
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderRight: '1px solid rgba(255, 255, 255, 0.08)', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'space-between', 
        padding: sidebarCollapsed ? '20px 10px' : '20px',
        overflow: 'hidden',
        boxShadow: '4px 0 24px rgba(0,0,0,0.15)',
        zIndex: 20
      }}>
        <div>
          {/* Collapse Trigger Button */}
          <button 
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)} 
            className="btn btn-secondary" 
            style={{ 
              padding: '6px', 
              marginBottom: '16px', 
              width: '100%', 
              justifyContent: 'center', 
              border: 'none', 
              backgroundColor: 'transparent', 
              color: 'var(--text-secondary)' 
            }}
            title={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>

          <div style={{ padding: sidebarCollapsed ? '0' : '10px', marginBottom: '30px', textAlign: sidebarCollapsed ? 'center' : 'left' }}>
            {settings.company_logo && (
              <img src={settings.company_logo} alt="Logo" style={{ maxHeight: '35px', maxWidth: '100%', objectFit: 'contain', marginBottom: '10px' }} onError={e => e.target.style.display = 'none'} />
            )}
            {!sidebarCollapsed && (
              <>
                <h2 style={{ fontSize: '1.6rem', background: 'linear-gradient(135deg, #a78bfa 0%, #6366f1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontWeight: '800' }}>{settings.company_name || 'LedgerPro'}</h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--success)', fontSize: '0.8rem', marginTop: '6px' }}>
                  <ShieldCheck size={12} />
                  <span>MySQL connected</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
                  <Store size={14} />
                  <span>Branch: {outlets.find(o => o.id === user?.outlet_id)?.name || 'Main Outlet'}</span>
                </div>
              </>
            )}
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {[
              { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={18} /> },
              { id: 'master', label: 'Master Data', icon: <Users size={18} /> },
              { id: 'invoices', label: 'Invoices & Sales', icon: <ShoppingCart size={18} /> },
              { id: 'bills', label: 'Bills & Purchases', icon: <Receipt size={18} /> },
              { id: 'payments', label: 'Payments ledger', icon: <Wallet size={18} /> },
              { id: 'stock', label: 'FIFO Inventory', icon: <Layers size={18} />, adminOnly: true },
              { id: 'reports', label: 'Reports', icon: <BarChart3 size={18} />, adminOnly: true },
              { id: 'settings', label: 'Settings', icon: <Settings size={18} /> },
            ].filter(item => !item.adminOnly || user?.role === 'Admin').map(item => (
              <button 
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className="btn"
                title={sidebarCollapsed ? item.label : undefined}
                style={{
                  justifyContent: sidebarCollapsed ? 'center' : 'flex-start',
                  background: currentView === item.id ? 'var(--accent-gradient)' : 'transparent',
                  color: currentView === item.id ? 'white' : 'var(--text-secondary)',
                  padding: sidebarCollapsed ? '12px' : '12px 16px',
                  borderRadius: 'var(--border-radius-sm)',
                  gap: sidebarCollapsed ? '0' : '10px',
                  boxShadow: currentView === item.id ? '0 4px 12px rgba(99, 102, 241, 0.3)' : 'none',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                {item.icon}
                {!sidebarCollapsed && <span>{item.label}</span>}
              </button>
            ))}
          </div>
        </div>

        {/* User Card */}
        <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '20px' }}>
          <button 
            onClick={() => setCurrentView('settings')}
            className="btn btn-secondary"
            style={{ width: '100%', marginBottom: '12px', justifyContent: 'center', fontSize: '0.85rem', padding: sidebarCollapsed ? '8px' : '10px' }}
            title="Theme & Settings"
          >
            {sidebarCollapsed ? (
              <Palette size={16} />
            ) : (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                <Palette size={16} />
                <span>Appearance</span>
              </span>
            )}
          </button>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: sidebarCollapsed ? 'center' : 'space-between', flexDirection: sidebarCollapsed ? 'column' : 'row', gap: sidebarCollapsed ? '12px' : '0' }}>
            {!sidebarCollapsed && (
              <div>
                <p style={{ fontWeight: '600', fontSize: '0.95rem' }}>{user?.name || 'User'}</p>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{user?.role || 'Store Staff'} • {user?.email}</p>
              </div>
            )}
            <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '8px' }} title="Logout">
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Workspace Wrapper */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        {/* Modern Glassmorphic App Header */}
        <header className="no-print" style={{
          height: '70px',
          background: 'rgba(15, 23, 42, 0.45)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 40px',
          zIndex: 10,
          boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
          flexShrink: 0
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.15em', fontWeight: 'bold' }}>TSL SWIFTBILL ERP</span>
            <span style={{ color: 'var(--text-muted)' }}>/</span>
            <span style={{ fontSize: '0.9rem', fontWeight: '700', textTransform: 'capitalize', color: 'var(--text-primary)' }}>{currentView === 'master' ? 'Master Data' : currentView}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--bg-secondary)', padding: '6px 14px', borderRadius: '20px', border: '1px solid var(--border-color)', fontSize: '0.82rem' }}>
              <Store size={14} style={{ color: 'var(--accent-primary)' }} />
              <span style={{ fontWeight: '600' }}>Active: {outlets.find(o => o.id === user?.outlet_id)?.name || 'Main Outlet'}</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--success)', background: 'var(--success-bg)', padding: '4px 10px', borderRadius: '12px' }}>
              <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--success)' }}></div>
              <span>Live DB</span>
            </div>
          </div>
        </header>

        {/* Content Workspace Area */}
        <div style={{ flex: 1, padding: '40px', overflowY: 'auto' }}>
          {currentView === 'dashboard' && <DashboardView stats={dashboardStats} invoices={invoices} bills={bills} outlets={outlets} selectedOutletFilter={selectedOutletFilter} setSelectedOutletFilter={setSelectedOutletFilter} user={user} settings={settings} />}
          {currentView === 'master' && <MasterDataView customers={customers} vendors={vendors} items={items} getHeaders={getHeaders} reload={loadAllData} settings={settings} />}
        {currentView === 'invoices' && <InvoicesView invoices={invoices} customers={customers} items={items} getHeaders={getHeaders} reload={loadAllData} settings={settings} outlets={outlets} user={user} />}
        {currentView === 'bills' && <BillsView bills={bills} vendors={vendors} items={items} getHeaders={getHeaders} reload={loadAllData} settings={settings} />}
        {currentView === 'payments' && <PaymentsView payments={payments} invoices={invoices} bills={bills} customers={customers} vendors={vendors} getHeaders={getHeaders} reload={loadAllData} />}
        {currentView === 'stock' && <StockView getHeaders={getHeaders} />}
        {currentView === 'reports' && <ReportsView getHeaders={getHeaders} />}
        {currentView === 'settings' && <SettingsView settings={settings} getHeaders={getHeaders} reload={loadAllData} token={token} outlets={outlets} theme={theme} setTheme={setTheme} user={user} />}
      </div>
      </div>
    </div>
  );
}

// ==================== VIEW: DASHBOARD ====================
function DashboardView({ stats, invoices, bills, outlets, selectedOutletFilter, setSelectedOutletFilter, user, settings }) {
  const [chartTab, setChartTab] = useState('Sales');
  const [chartPeriod, setChartPeriod] = useState('Day Wise');

  if (!stats) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px', flexDirection: 'column', gap: '16px' }}>
      <Activity size={32} style={{ color: 'var(--accent-primary)', opacity: 0.5 }} />
      <p style={{ color: 'var(--text-secondary)' }}>Loading analytics...</p>
    </div>
  );

  const sales = stats.sales || 0;
  const purchases = stats.purchases || 0;
  const receivables = stats.receivables || 0;
  const payables = Math.max(0, purchases - sales * 0.15);
  const profit = sales - purchases;
  const profitPct = sales > 0 ? ((profit / sales) * 100).toFixed(1) : 0;

  const monthlySales = stats.monthlySales || [];
  const monthlyPurchases = stats.monthlyPurchases || [];
  const hasRealData = monthlySales.length > 0;

  const getPoints = (dataList) => {
    if (dataList.length === 0) return [10, 20, 15, 30, 25, 40];
    const maxVal = Math.max(...dataList.map(d => d.total), 1000);
    return dataList.map(d => (d.total / maxVal) * 80 + 10);
  };

  const salesPoints = hasRealData ? getPoints(monthlySales) : [35, 52, 41, 68, 58, 77, 62];
  const purchPoints = hasRealData ? getPoints(monthlyPurchases) : [20, 30, 28, 40, 35, 50, 38];
  const expensePoints = salesPoints.map(s => s * 0.25);

  const months = hasRealData 
    ? monthlySales.map(m => {
        const [year, month] = m.month.split('-');
        const date = new Date(year, parseInt(month) - 1, 1);
        return date.toLocaleDateString('en-IN', { month: 'short' });
      })
    : ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  const toSvgPath = (pts) => {
    const maxY = 100; const w = 100; const h = 100;
    return pts.map((v, i) => {
      const x = (i / (pts.length - 1)) * w;
      const y = h - (v / maxY) * h;
      return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
    }).join(' ');
  };

  const activePoints = chartTab === 'Sales' ? salesPoints : chartTab === 'Purchase' ? purchPoints : expensePoints;
  const activeColor  = chartTab === 'Sales' ? 'var(--accent-primary)' : chartTab === 'Purchase' ? 'var(--warning)' : 'var(--danger)';

  // Upcoming due invoices
  const upcomingInvoices = invoices.filter(inv => {
    if (inv.status === 'Paid') return false;
    const dueDate = new Date(inv.due_date);
    const diff = (dueDate - new Date()) / (1000 * 60 * 60 * 24);
    return diff >= 0 && diff <= 7;
  });

  // Payment method breakdown
  const payMethodBreakdown = {};
  invoices.forEach(inv => {
    // simulate
  });
  const payMethods = [
    { label: 'Bank Transfer', pct: 48, color: '#6366f1' },
    { label: 'Cash', pct: 28, color: '#10b981' },
    { label: 'UPI', pct: 18, color: '#f59e0b' },
    { label: 'Cheque', pct: 6, color: '#0ea5e9' },
  ];

  return (
    <div>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '4px' }}>Welcome Back{user ? `, ${user.name.split(' ')[0]}` : ''}!</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{settings?.company_name || 'LedgerPro'} — Business Intelligence Overview</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {user?.role === 'Admin' && (
            <select 
              value={selectedOutletFilter} 
              onChange={e => setSelectedOutletFilter(e.target.value)}
              className="form-control"
              style={{ width: '180px', marginBottom: 0 }}
            >
              <option value="all">All Branches</option>
              {outlets.map(o => (
                <option key={o.id} value={o.id}>{o.name}</option>
              ))}
            </select>
          )}
          <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '8px 14px', fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Activity size={14} />
            {new Date().toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })}
          </div>
        </div>
      </div>

      {/* ── Row 1: 4 KPI Cards ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        {/* Total Sales */}
        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'rgba(99,102,241,0.15)' }}>
            <ShoppingCart size={22} style={{ color: '#6366f1' }} />
          </div>
          <div>
            <p className="kpi-label">Total Sales</p>
            <p className="kpi-value">₹{(sales / 100).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',')||'0'}</p>
            <p className="kpi-trend up"><ArrowUpRight size={13} /> 5% Last Month</p>
          </div>
        </div>
        {/* Total Purchase */}
        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'rgba(245,158,11,0.15)' }}>
            <Receipt size={22} style={{ color: '#f59e0b' }} />
          </div>
          <div>
            <p className="kpi-label">Total Purchase</p>
            <p className="kpi-value">₹{(purchases / 100).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',')||'0'}</p>
            <p className="kpi-trend up"><ArrowUpRight size={13} /> 2% Last Month</p>
          </div>
        </div>
        {/* Receivable */}
        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'rgba(16,185,129,0.15)' }}>
            <TrendingUp size={22} style={{ color: '#10b981' }} />
          </div>
          <div>
            <p className="kpi-label">Receivable</p>
            <p className="kpi-value">₹{receivables.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
            <p className="kpi-trend up"><ArrowUpRight size={13} /> 10% Last Month</p>
          </div>
        </div>
        {/* Total Payable */}
        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'rgba(239,68,68,0.15)' }}>
            <TrendingDown size={22} style={{ color: '#ef4444' }} />
          </div>
          <div>
            <p className="kpi-label">Total Payable</p>
            <p className="kpi-value">₹{payables.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
            <p className="kpi-trend down"><ArrowDownRight size={13} /> 5% Last Month</p>
          </div>
        </div>
      </div>

      {/* ── Row 2: Line Chart + Period Selector ── */}
      <div className="bi-chart-panel" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div className="bi-chart-tabs">
            {['Sales', 'Purchase', 'Expense'].map(tab => (
              <button key={tab} className={`bi-chart-tab${chartTab === tab ? ' active' : ''}`} onClick={() => setChartTab(tab)}>
                {tab}
              </button>
            ))}
          </div>
          <select className="form-control" value={chartPeriod} onChange={e => setChartPeriod(e.target.value)} style={{ width: '130px', marginBottom: 0, fontSize: '0.85rem' }}>
            <option>Day Wise</option>
            <option>Week Wise</option>
            <option>Month Wise</option>
          </select>
        </div>

        {/* SVG Multi-Line Chart */}
        <div style={{ position: 'relative', height: '200px', paddingLeft: '8px' }}>
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ width: '100%', height: '100%', overflow: 'visible' }} className="chart-svg-area">
            {/* Grid Lines */}
            {[25, 50, 75].map(y => (
              <line key={y} x1="0" y1={100 - y} x2="100" y2={100 - y} stroke="var(--border-color)" strokeWidth="0.3" strokeDasharray="2,2" />
            ))}
            {/* Background series (dim) */}
            {chartTab !== 'Sales' && (
              <path d={toSvgPath(salesPoints)} fill="none" stroke="#6366f1" strokeWidth="0.8" opacity="0.2" />
            )}
            {chartTab !== 'Purchase' && (
              <path d={toSvgPath(purchPoints)} fill="none" stroke="#f59e0b" strokeWidth="0.8" opacity="0.2" />
            )}
            {chartTab !== 'Expense' && (
              <path d={toSvgPath(expensePoints)} fill="none" stroke="#ef4444" strokeWidth="0.8" opacity="0.2" />
            )}
            {/* Active series */}
            <path d={toSvgPath(activePoints)} fill="none" stroke={activeColor} strokeWidth="2" />
            {activePoints.map((v, i) => {
              const x = (i / (activePoints.length - 1)) * 100;
              const y = 100 - (v / 100) * 100;
              return <circle key={i} cx={x.toFixed(1)} cy={y.toFixed(1)} r="1.5" fill={activeColor} />;
            })}
          </svg>
          {/* X-axis labels */}
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {months.map((m, idx) => <span key={idx}>{m}</span>)}
          </div>
        </div>
      </div>

      {/* ── Row 3: Sales Conversion + P&L ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '20px', marginBottom: '24px' }}>
        {/* Sales Conversion Bar Chart */}
        <div className="bi-chart-panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '700' }}>Sales Conversion Summary</h3>
            <div style={{ display: 'flex', gap: '12px', fontSize: '0.78rem', color: 'var(--text-secondary)', alignItems: 'center' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><span style={{ width: '10px', height: '10px', borderRadius: '2px', background: '#6366f1', display: 'inline-block' }}></span>Sales</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><span style={{ width: '10px', height: '10px', borderRadius: '2px', background: '#a5b4fc', display: 'inline-block' }}></span>Estimates</span>
            </div>
          </div>
          {/* Stacked bars */}
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '6px', height: '120px', paddingBottom: '8px', borderBottom: '1px solid var(--border-color)' }}>
            {[{s:72,e:28},{s:58,e:42},{s:80,e:20},{s:65,e:35},{s:90,e:10},{s:55,e:45},{s:78,e:22},{s:60,e:40}].map((d, i) => (
              <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1px', height: '100%', justifyContent: 'flex-end' }}>
                <div style={{ width: '100%', height: `${d.e * 0.7}%`, background: '#a5b4fc', borderRadius: '3px 3px 0 0', opacity: 0.7 }}></div>
                <div style={{ width: '100%', height: `${d.s * 0.7}%`, background: '#6366f1', borderRadius: '3px 3px 0 0' }}></div>
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px' }}>
            {['1','2','3','4','5','6','7','8'].map(d => (
              <span key={d} style={{ fontSize: '0.7rem', color: 'var(--text-muted)', flex: 1, textAlign: 'center' }}>{d} {new Date().toLocaleDateString('en-IN', { month: 'short' })}</span>
            ))}
          </div>
        </div>

        {/* P&L Card */}
        <div className="pl-card">
          <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '16px' }}>Profit &amp; Loss</h3>
          <div className="pl-row" style={{ background: 'rgba(99,102,241,0.05)' }}>
            <div className="pl-row-icon" style={{ background: 'rgba(99,102,241,0.15)' }}>
              <DollarSign size={20} style={{ color: '#6366f1' }} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '2px' }}>Revenue</p>
              <p className="pl-amount" style={{ color: '#6366f1' }}>₹{sales.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
            </div>
          </div>
          <div style={{ textAlign: 'center', fontSize: '1.2rem', color: 'var(--text-muted)', margin: '-4px 0' }}>−</div>
          <div className="pl-row" style={{ background: 'rgba(239,68,68,0.05)' }}>
            <div className="pl-row-icon" style={{ background: 'rgba(239,68,68,0.15)' }}>
              <CreditCard size={20} style={{ color: '#ef4444' }} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '2px' }}>Expense</p>
              <p className="pl-amount" style={{ color: '#ef4444' }}>₹{purchases.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
            </div>
          </div>
          <div className="pl-row" style={{ marginTop: '4px', borderColor: profit >= 0 ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)', background: profit >= 0 ? 'rgba(16,185,129,0.05)' : 'rgba(239,68,68,0.05)' }}>
            <div className="pl-row-icon" style={{ background: profit >= 0 ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)' }}>
              <TrendingUp size={20} style={{ color: profit >= 0 ? '#10b981' : '#ef4444' }} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '2px' }}>Profit</p>
              <p className="pl-amount" style={{ color: profit >= 0 ? '#10b981' : '#ef4444' }}>₹{Math.abs(profit).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Row 4: Payment Bifurcation + Cashflow ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        {/* Payment Bifurcation */}
        <div className="bi-chart-panel">
          <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '16px' }}>Payment Bifurcation</h3>
          {payMethods.map(pm => (
            <div key={pm.label} className="bar-chart-row">
              <span className="bar-chart-label">{pm.label}</span>
              <div className="bar-chart-track">
                <div className="bar-chart-fill" style={{ width: `${pm.pct}%`, background: pm.color }}></div>
              </div>
              <span className="bar-chart-val">{pm.pct}%</span>
            </div>
          ))}
        </div>

        {/* Cashflow Summary */}
        <div className="bi-chart-panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '700' }}>Cashflow</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Main Account</span>
          </div>
          {[
            { label: 'Opening Balance', val: 0, color: 'var(--text-secondary)', icon: <DollarSign size={16} /> },
            { label: 'Incoming (+)', val: sales, color: '#10b981', icon: <ArrowUpRight size={16} /> },
            { label: 'Outgoing (−)', val: purchases, color: '#ef4444', icon: <ArrowDownRight size={16} /> },
            { label: 'Net Balance', val: sales - purchases, color: sales >= purchases ? '#10b981' : '#ef4444', icon: <Activity size={16} /> },
          ].map(row => (
            <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                <span style={{ color: row.color }}>{row.icon}</span>
                {row.label}
              </div>
              <span style={{ fontWeight: '700', color: row.color }}>₹{Math.abs(row.val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Row 5: Upcoming Due Invoices Table ── */}
      <div className="bi-chart-panel">
        <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '16px' }}>Upcoming Due Invoices (Next 7 Days)</h3>
        <div className="table-container" style={{ marginTop: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Date</th>
                <th>Due Date</th>
                <th>Customer</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {upcomingInvoices.map(inv => (
                <tr key={inv.id}>
                  <td><strong>{inv.invoice_number}</strong></td>
                  <td>{new Date(inv.date).toLocaleDateString()}</td>
                  <td>{new Date(inv.due_date).toLocaleDateString()}</td>
                  <td>{inv.customer_name}</td>
                  <td style={{ fontWeight: 'bold' }}>₹{inv.grand_total.toFixed(2)}</td>
                  <td><span style={{ padding: '2px 10px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: '600', background: 'var(--warning-bg)', color: 'var(--warning)' }}>{inv.status}</span></td>
                </tr>
              ))}
              {upcomingInvoices.length === 0 && (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '24px' }}>
                    No due invoices in the next 7 days.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ==================== VIEW: MASTER DATA ====================
function MasterDataView({ customers, vendors, items, getHeaders, reload, settings }) {
  const [activeTab, setActiveTab] = useState('items');
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedEntity, setSelectedEntity] = useState(null); // for editing

  // Items Form States
  const [itemName, setItemName] = useState('');
  const [itemSku, setItemSku] = useState('');
  const [itemHsn, setItemHsn] = useState('');
  const [itemGst, setItemGst] = useState(18);
  const [itemUnit, setItemUnit] = useState('pcs');
  const [itemSelling, setItemSelling] = useState(0);
  const [itemSp1, setItemSp1] = useState(0);
  const [itemSp2, setItemSp2] = useState(0);
  const [itemSp3, setItemSp3] = useState(0);
  const [itemPurchase, setItemPurchase] = useState(0);
  const [itemReorder, setItemReorder] = useState(5);
  const [itemOpening, setItemOpening] = useState(0);
  const [itemImageUrl, setItemImageUrl] = useState('');
  const [itemIsSellable, setItemIsSellable] = useState(true);

  // Customer/Vendor Form States
  const [entName, setEntName] = useState('');
  const [entEmail, setEntEmail] = useState('');
  const [entPhone, setEntPhone] = useState('');
  const [entAddress, setEntAddress] = useState('');
  const [entGstin, setEntGstin] = useState('');
  const [entState, setEntState] = useState('');
  const [custType, setCustType] = useState('Type 1');

  // CSV file state
  const [csvFile, setCsvFile] = useState(null);
  const [csvMsg, setCsvMsg] = useState('');

  const openNewForm = () => {
    setSelectedEntity(null);
    setItemName(''); setItemSku(''); setItemHsn(''); setItemGst(18); setItemUnit('pcs');
    setItemSelling(0); setItemSp1(0); setItemSp2(0); setItemSp3(0); setItemPurchase(0); setItemReorder(5); setItemOpening(0);
    setItemImageUrl(''); setItemIsSellable(true);
    setEntName(''); setEntEmail(''); setEntPhone(''); setEntAddress(''); setEntGstin(''); setEntState(''); setCustType('Type 1');
    setShowModal(true);
  };

  const handleEdit = (ent) => {
    setSelectedEntity(ent);
    if (activeTab === 'items') {
      setItemName(ent.name); setItemSku(ent.sku); setItemHsn(ent.hsn_sac); setItemGst(ent.gst_rate); setItemUnit(ent.unit);
      setItemSelling(ent.selling_price); setItemSp1(ent.sp1); setItemSp2(ent.sp2); setItemSp3(ent.sp3); setItemPurchase(ent.purchase_price);
      setItemReorder(ent.reorder_point); setItemOpening(ent.opening_stock);
      setItemImageUrl(ent.image_url || '');
      setItemIsSellable(ent.is_sellable === undefined ? true : (ent.is_sellable ? true : false));
    } else {
      setEntName(ent.name); setEntEmail(ent.email || ''); setEntPhone(ent.phone || ''); setEntAddress(ent.address || '');
      setEntGstin(ent.gstin || ''); setEntState(ent.state || ''); setCustType(ent.customer_type || 'Type 1');
    }
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const endpoint = selectedEntity 
      ? `${API_BASE}/${activeTab}/${selectedEntity.id}`
      : `${API_BASE}/${activeTab}`;
    const method = selectedEntity ? 'PUT' : 'POST';

    let body = {};
    if (activeTab === 'items') {
      body = {
        name: itemName, sku: itemSku, hsn_sac: itemHsn, gst_rate: parseFloat(itemGst), unit: itemUnit,
        selling_price: parseFloat(itemSelling), sp1: parseFloat(itemSp1), sp2: parseFloat(itemSp2), sp3: parseFloat(itemSp3),
        purchase_price: parseFloat(itemPurchase), reorder_point: parseFloat(itemReorder), opening_stock: parseFloat(itemOpening),
        image_url: itemImageUrl, is_sellable: itemIsSellable
      };
    } else if (activeTab === 'customers') {
      body = { name: entName, email: entEmail, phone: entPhone, address: entAddress, gstin: entGstin, state: entState, customer_type: custType };
    } else {
      body = { name: entName, email: entEmail, phone: entPhone, address: entAddress, gstin: entGstin, state: entState };
    }

    try {
      const res = await fetch(endpoint, {
        method,
        headers: getHeaders(),
        body: JSON.stringify(body)
      });
      if (res.ok) {
        setShowModal(false);
        reload();
      } else {
        const d = await res.json();
        alert(d.error || 'Failed to save record.');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this record?')) return;
    try {
      const res = await fetch(`${API_BASE}/${activeTab}/${id}`, {
        method: 'DELETE',
        headers: getHeaders()
      });
      if (res.ok) reload();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleCsvUpload = async (e) => {
    e.preventDefault();
    if (!csvFile) return;
    const formData = new FormData();
    formData.append('file', csvFile);

    try {
      const res = await fetch(`${API_BASE}/items/import`, {
        method: 'POST',
        headers: { 'Authorization': getHeaders()['Authorization'] },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setCsvMsg(data.message);
        reload();
      } else {
        setCsvMsg('Error: ' + data.error);
      }
    } catch (err) {
      setCsvMsg('Upload failed.');
    }
  };

  // Filter lists based on search
  const query = searchQuery.toLowerCase();
  const filteredItems = items.filter(x => x.name.toLowerCase().includes(query) || (x.sku && x.sku.toLowerCase().includes(query)));
  const filteredCustomers = customers.filter(x => x.name.toLowerCase().includes(query) || (x.email && x.email.toLowerCase().includes(query)));
  const filteredVendors = vendors.filter(x => x.name.toLowerCase().includes(query) || (x.email && x.email.toLowerCase().includes(query)));

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>Master Data Catalog</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Manage your enterprise items, customer directory, and vendor lists.</p>
        </div>
        <button onClick={openNewForm} className="btn btn-primary">
          <Plus size={18} />
          <span>Add New {activeTab === 'items' ? 'Item' : activeTab === 'customers' ? 'Customer' : 'Vendor'}</span>
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', marginBottom: '24px', gap: '16px' }}>
        {['items', 'customers', 'vendors'].map(tab => (
          <button 
            key={tab} 
            onClick={() => { setActiveTab(tab); setSearchQuery(''); }}
            style={{
              background: 'none', border: 'none', borderBottom: activeTab === tab ? '2px solid var(--accent-primary)' : 'none',
              color: activeTab === tab ? 'var(--text-primary)' : 'var(--text-secondary)', padding: '12px 16px', cursor: 'pointer',
              fontWeight: activeTab === tab ? '600' : '400', textTransform: 'capitalize'
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Bulk CSV Upload Widget for Items */}
      {activeTab === 'items' && (
        <div className="card" style={{ marginBottom: '24px', padding: '16px' }}>
          <h4 style={{ marginBottom: '12px' }}>Bulk Import Items via CSV</h4>
          <form onSubmit={handleCsvUpload} style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <input type="file" accept=".csv" onChange={e => setCsvFile(e.target.files[0])} style={{ color: 'var(--text-secondary)' }} />
            <button className="btn btn-secondary" type="submit">
              <Upload size={16} />
              <span>Upload CSV</span>
            </button>
            {csvMsg && <span style={{ fontSize: '0.9rem', color: 'var(--info)' }}>{csvMsg}</span>}
          </form>
        </div>
      )}

      {/* Search filter */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', padding: '10px 16px', borderRadius: 'var(--border-radius-sm)', maxWidth: '400px', marginBottom: '24px' }}>
        <Search size={18} color="var(--text-secondary)" />
        <input type="text" placeholder={`Search ${activeTab}...`} value={searchQuery} onChange={e => setSearchQuery(e.target.value)} style={{ background: 'none', border: 'none', outline: 'none', width: '100%' }} />
      </div>

      {/* Data tables */}
      {activeTab === 'items' && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Image</th>
                <th>Item Name</th>
                <th>SKU</th>
                <th>HSN/SAC</th>
                <th>GST Rate</th>
                <th>Unit</th>
                <th>SP (Base)</th>
                <th>{settings.sp1_label || 'SP1 (Tier 1)'}</th>
                <th>{settings.sp2_label || 'SP2 (Tier 2)'}</th>
                <th>{settings.sp3_label || 'SP3 (Tier 3)'}</th>
                <th>Purchase rate</th>
                <th>Stock hand</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map(item => (
                <tr key={item.id}>
                  <td>
                    <div style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border-color)', borderRadius: '4px', overflow: 'hidden', backgroundColor: 'var(--bg-tertiary)' }}>
                      {item.image_url ? (
                        <img src={item.image_url} alt="" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} onError={e => e.target.style.display = 'none'} />
                      ) : (
                        <Package size={18} color="var(--text-secondary)" />
                      )}
                    </div>
                  </td>
                  <td><strong>{item.name}</strong></td>
                  <td>{item.sku}</td>
                  <td>{item.hsn_sac}</td>
                  <td>{item.gst_rate}%</td>
                  <td>{item.unit}</td>
                  <td>₹{item.selling_price}</td>
                  <td>₹{item.sp1}</td>
                  <td>₹{item.sp2}</td>
                  <td>₹{item.sp3}</td>
                  <td>₹{item.purchase_price}</td>
                  <td style={{ color: item.stock_on_hand <= item.reorder_point ? 'var(--warning)' : 'inherit' }}>{item.stock_on_hand}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button onClick={() => handleEdit(item)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Edit</button>
                      <button onClick={() => handleDelete(item.id)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'customers' && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Customer Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>GSTIN</th>
                <th>State</th>
                <th>Pricing Tier</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredCustomers.map(cust => (
                <tr key={cust.id}>
                  <td><strong>{cust.name}</strong></td>
                  <td>{cust.email}</td>
                  <td>{cust.phone}</td>
                  <td>{cust.gstin}</td>
                  <td>{cust.state}</td>
                  <td><span style={{ background: 'var(--info-bg)', color: 'var(--info)', padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem' }}>{cust.customer_type}</span></td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button onClick={() => handleEdit(cust)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Edit</button>
                      <button onClick={() => handleDelete(cust.id)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'vendors' && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Vendor Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>GSTIN</th>
                <th>State</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredVendors.map(v => (
                <tr key={v.id}>
                  <td><strong>{v.name}</strong></td>
                  <td>{v.email}</td>
                  <td>{v.phone}</td>
                  <td>{v.gstin}</td>
                  <td>{v.state}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button onClick={() => handleEdit(v)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Edit</button>
                      <button onClick={() => handleDelete(v.id)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal Dialog for Add/Edit */}
      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div className="card" style={{ width: '100%', maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto' }}>
            <h3 style={{ marginBottom: '20px' }}>{selectedEntity ? 'Edit' : 'Create'} {activeTab === 'items' ? 'Item' : activeTab === 'customers' ? 'Customer' : 'Vendor'}</h3>
            <form onSubmit={handleSubmit}>
              {activeTab === 'items' ? (
                <>
                  <div className="form-group">
                    <label className="form-label">Item Name</label>
                    <input className="form-control" type="text" value={itemName} onChange={e => setItemName(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Product Image URL</label>
                    <input className="form-control" type="text" value={itemImageUrl} onChange={e => setItemImageUrl(e.target.value)} placeholder="https://example.com/product.png" />
                  </div>
                  <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                    <input type="checkbox" checked={itemIsSellable} onChange={e => setItemIsSellable(e.target.checked)} id="is_sellable_checkbox" style={{ width: 'auto', cursor: 'pointer', margin: 0 }} />
                    <label htmlFor="is_sellable_checkbox" style={{ margin: 0, fontWeight: '600', cursor: 'pointer', fontSize: '0.9rem' }}>Item is Sellable</label>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div className="form-group">
                      <label className="form-label">SKU</label>
                      <input className="form-control" type="text" value={itemSku} onChange={e => setItemSku(e.target.value)} />
                    </div>
                    <div className="form-group">
                      <label className="form-label">HSN/SAC</label>
                      <input className="form-control" type="text" value={itemHsn} onChange={e => setItemHsn(e.target.value)} />
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div className="form-group">
                      <label className="form-label">GST Rate (%)</label>
                      <input className="form-control" type="number" value={itemGst} onChange={e => setItemGst(e.target.value)} />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Unit</label>
                      <input className="form-control" type="text" value={itemUnit} onChange={e => setItemUnit(e.target.value)} />
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div className="form-group">
                      <label className="form-label">Selling Price (Base)</label>
                      <input className="form-control" type="number" value={itemSelling} onChange={e => setItemSelling(e.target.value)} />
                    </div>
                    <div className="form-group">
                      <label className="form-label">{settings.sp1_label || 'SP1 (Tier 1)'}</label>
                      <input className="form-control" type="number" value={itemSp1} onChange={e => setItemSp1(e.target.value)} />
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div className="form-group">
                      <label className="form-label">{settings.sp2_label || 'SP2 (Tier 2)'}</label>
                      <input className="form-control" type="number" value={itemSp2} onChange={e => setItemSp2(e.target.value)} />
                    </div>
                    <div className="form-group">
                      <label className="form-label">{settings.sp3_label || 'SP3 (Tier 3)'}</label>
                      <input className="form-control" type="number" value={itemSp3} onChange={e => setItemSp3(e.target.value)} />
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '16px' }}>
                    <div className="form-group">
                      <label className="form-label">Purchase Price</label>
                      <input className="form-control" type="number" value={itemPurchase} onChange={e => setItemPurchase(e.target.value)} />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Reorder Limit</label>
                      <input className="form-control" type="number" value={itemReorder} onChange={e => setItemReorder(e.target.value)} />
                    </div>
                  </div>
                  {!selectedEntity && (
                    <div className="form-group">
                      <label className="form-label">Opening Stock Quantity</label>
                      <input className="form-control" type="number" value={itemOpening} onChange={e => setItemOpening(e.target.value)} />
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div className="form-group">
                    <label className="form-label">Name</label>
                    <input className="form-control" type="text" value={entName} onChange={e => setEntName(e.target.value)} required />
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div className="form-group">
                      <label className="form-label">Email</label>
                      <input className="form-control" type="email" value={entEmail} onChange={e => setEntEmail(e.target.value)} />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Phone</label>
                      <input className="form-control" type="text" value={entPhone} onChange={e => setEntPhone(e.target.value)} />
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Billing Address</label>
                    <textarea className="form-control" rows="2" value={entAddress} onChange={e => setEntAddress(e.target.value)}></textarea>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div className="form-group">
                      <label className="form-label">GSTIN</label>
                      <input className="form-control" type="text" value={entGstin} onChange={e => setEntGstin(e.target.value.toUpperCase())} />
                      {entGstin && !/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(entGstin) && (
                        <small style={{ color: '#f97316', marginTop: '4px', display: 'block' }}>⚠️ Invalid GSTIN format</small>
                      )}
                    </div>
                    <div className="form-group">
                      <label className="form-label">State</label>
                      <input className="form-control" type="text" value={entState} onChange={e => setEntState(e.target.value)} placeholder="e.g. Haryana" />
                    </div>
                  </div>
                  {activeTab === 'customers' && (
                    <div className="form-group">
                      <label className="form-label">Pricing Tier (Customer Type)</label>
                      <select className="form-control" value={custType} onChange={e => setCustType(e.target.value)}>
                        <option value="Type 1">Type 1 (Uses SP1)</option>
                        <option value="Type 2">Type 2 (Uses SP2)</option>
                        <option value="Type 3">Type 3 (Uses SP3)</option>
                        <option value="Base">Base (Uses standard Rate)</option>
                      </select>
                    </div>
                  )}
                </>
              )}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">Cancel</button>
                <button type="submit" className="btn btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function getInvoiceStatus(inv) {
  if (!inv) return 'Sent';
  if (inv.status === 'Draft' || inv.status === 'Paid' || inv.status === 'Partially Paid') {
    return inv.status;
  }
  if (inv.due_date) {
    const todayStr = new Date().toISOString().split('T')[0];
    const dueDateStr = new Date(inv.due_date).toISOString().split('T')[0];
    if (dueDateStr < todayStr) {
      return 'Overdue';
    }
  }
  return inv.status === 'Due' ? 'Due' : 'Sent';
}

// ==================== VIEW: INVOICES ====================
function InvoicesView({ invoices, customers, items, getHeaders, reload, settings, outlets, user }) {
  const [showCreate, setShowCreate] = useState(false);
  const [editingInvoiceId, setEditingInvoiceId] = useState(null);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [printLayout, setPrintLayout] = useState('a4'); // 'a4' | 'a5' | 'thermal'

  // Form Fields
  const [customerId, setCustomerId] = useState('');
  const [invDate, setInvDate] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [notes, setNotes] = useState('');
  const [salesperson, setSalesperson] = useState('');
  const [invoiceItems, setInvoiceItems] = useState([{ item_id: '', quantity: 1, rate: 0, discount_percent: 0 }]);
  const [roundOff, setRoundOff] = useState(0);
  const [selectedOutlet, setSelectedOutlet] = useState(user?.outlet_id || 1);
  const [orderNumber, setOrderNumber] = useState('');
  const [terms, setTerms] = useState('');
  const [subject, setSubject] = useState('');
  const [customerNotes, setCustomerNotes] = useState('');
  const [termsConditions, setTermsConditions] = useState('');
  const [tdsAmount, setTdsAmount] = useState(0);
  const [tcsAmount, setTcsAmount] = useState(0);
  const [status, setStatus] = useState('Sent');

  const applyTermsPreset = (days, label) => {
    const baseDate = invDate ? new Date(invDate) : new Date();
    const d = new Date(baseDate);
    d.setDate(d.getDate() + days);
    const newDueDate = d.toISOString().split('T')[0];
    setDueDate(newDueDate);
    setTerms(label || (days === 0 ? 'Due on Receipt' : `Net ${days}`));
  };

  const handlePrintThermal = () => {
    if (!selectedInvoice) return;
    const printWindow = window.open('', '_blank', 'width=320,height=600');
    const itemsHtml = selectedInvoice.items.map(ii => `
      <tr>
        <td style="padding: 4px 0; font-size: 12px; font-family: monospace;">${ii.item_name}<br/>${ii.quantity} x ₹${ii.rate}</td>
        <td style="text-align: right; padding: 4px 0; font-size: 12px; font-family: monospace;">₹${ii.amount.toFixed(2)}</td>
      </tr>
    `).join('');

    const upiId = selectedInvoice.invoice.outlet_upi_id || settings.company_upi_id;
    const upiUri = upiId ? `upi://pay?pa=${upiId}&pn=${encodeURIComponent(settings.company_name || 'LedgerPro')}&am=${selectedInvoice.invoice.grand_total.toFixed(2)}&cu=INR&tn=Invoice-${selectedInvoice.invoice.invoice_number}` : '';
    const qrUrl = upiUri ? `https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=${encodeURIComponent(upiUri)}` : '';

    const htmlContent = `
      <html>
        <head>
          <title>Receipt ${selectedInvoice.invoice.invoice_number}</title>
          <style>
            @page { margin: 0; }
            body { 
              font-family: 'Courier New', Courier, monospace; 
              width: 260px; 
              margin: 0 auto; 
              padding: 10px; 
              color: #000;
              background-color: #fff;
            }
            .center { text-align: center; }
            .divider { border-top: 1px dashed #000; margin: 8px 0; }
            table { width: 100%; border-collapse: collapse; }
            .totals td { font-size: 12px; padding: 2px 0; }
          </style>
        </head>
        <body>
          <div class="center">
            <h3 style="margin: 4px 0;">${settings.company_name || 'LedgerPro'}</h3>
            <p style="font-size: 11px; margin: 2px 0;">${selectedInvoice.invoice.outlet_name || 'Main Outlet'}</p>
            <p style="font-size: 10px; margin: 2px 0;">${selectedInvoice.invoice.outlet_address || settings.company_address || ''}</p>
            <p style="font-size: 10px; margin: 2px 0;">GSTIN: ${selectedInvoice.invoice.outlet_gstin || settings.company_gstin || ''}</p>
          </div>
          <div class="divider"></div>
          <p style="font-size: 11px; margin: 2px 0;">INV: ${selectedInvoice.invoice.invoice_number}</p>
          <p style="font-size: 11px; margin: 2px 0;">Date: ${new Date(selectedInvoice.invoice.date).toLocaleDateString()}</p>
          <p style="font-size: 11px; margin: 2px 0;">Client: ${selectedInvoice.invoice.customer_name}</p>
          <div class="divider"></div>
          <table>
            <thead>
              <tr style="border-bottom: 1px dashed #000;">
                <th style="text-align: left; font-size: 11px; padding-bottom: 4px;">Item</th>
                <th style="text-align: right; font-size: 11px; padding-bottom: 4px;">Total</th>
              </tr>
            </thead>
            <tbody>
              ${itemsHtml}
            </tbody>
          </table>
          <div class="divider"></div>
          <table class="totals">
            <tr>
              <td>Subtotal:</td>
              <td style="text-align: right;">₹${selectedInvoice.invoice.subtotal.toFixed(2)}</td>
            </tr>
            <tr>
              <td>GST Tax:</td>
              <td style="text-align: right;">₹${selectedInvoice.invoice.tax_amount.toFixed(2)}</td>
            </tr>
            ${selectedInvoice.invoice.round_off !== 0 ? `
              <tr>
                <td>Round-off:</td>
                <td style="text-align: right;">₹${selectedInvoice.invoice.round_off.toFixed(2)}</td>
              </tr>
            ` : ''}
            <tr style="font-weight: bold; font-size: 13px;">
              <td style="padding-top: 4px;">GRAND TOTAL:</td>
              <td style="text-align: right; padding-top: 4px;">₹${selectedInvoice.invoice.grand_total.toFixed(2)}</td>
            </tr>
          </table>
          ${qrUrl ? `
            <div class="divider"></div>
            <div class="center" style="margin-top: 8px;">
              <p style="font-size: 10px; margin: 2px 0 6px 0;">Scan to Pay</p>
              <img src="${qrUrl}" style="width: 100px; height: 100px;" />
              <p style="font-size: 9px; margin-top: 4px;">UPI ID: ${upiId}</p>
            </div>
          ` : ''}
          <div class="divider"></div>
          <div class="center" style="font-size: 10px; margin-top: 10px;">
            Thank you for your business!
          </div>
          <script>
            window.onload = function() {
              window.print();
              setTimeout(function() { window.close(); }, 500);
            }
          </script>
        </body>
      </html>
    `;
    printWindow.document.write(htmlContent);
    printWindow.document.close();
  };

  const handleCustomerChange = (val) => {
    setCustomerId(val);
    const customer = customers.find(c => c.id === parseInt(val));
    if (customer) {
      const sp1Label = settings.sp1_label || 'Type 1';
      const sp2Label = settings.sp2_label || 'Type 2';
      const sp3Label = settings.sp3_label || 'Type 3';
      
      let rateType = 'selling_price';
      const cType = customer.customer_type;
      if (cType === 'Type 1' || cType === sp1Label) rateType = 'sp1';
      else if (cType === 'Type 2' || cType === sp2Label) rateType = 'sp2';
      else if (cType === 'Type 3' || cType === sp3Label) rateType = 'sp3';

      const updated = invoiceItems.map(ii => {
        if (!ii.item_id) return ii;
        const it = items.find(itm => itm.id === parseInt(ii.item_id));
        let rate = 0;
        if (it) {
          if (rateType === 'selling_price') rate = it.selling_price;
          else if (rateType === 'sp1') rate = it.sp1 || it.selling_price;
          else if (rateType === 'sp2') rate = it.sp2 || it.selling_price;
          else if (rateType === 'sp3') rate = it.sp3 || it.selling_price;
        }
        return { ...ii, rate_type: rateType, rate };
      });
      setInvoiceItems(updated);
    }
  };

  const handleOutletChange = (val) => {
    setSelectedOutlet(val);
    const customer = customers.find(c => c.id === parseInt(customerId));
    const updated = invoiceItems.map(ii => {
      if (!ii.item_id) return ii;
      const it = items.find(itm => itm.id === parseInt(ii.item_id));
      return { ...ii, rate: getPriceForOutletAndCustomer(it, val, customer?.customer_type) };
    });
    setInvoiceItems(updated);
  };

  const getPriceForOutletAndCustomer = (item, outletId, custType) => {
    if (!item) return 0;
    const outlet = outlets.find(o => o.id === parseInt(outletId));
    const pType = outlet ? outlet.pricing_type : 'Base';

    if (pType === 'SP1') return item.sp1 || item.selling_price;
    if (pType === 'SP2') return item.sp2 || item.selling_price;
    if (pType === 'SP3') return item.sp3 || item.selling_price;

    const sp1Label = settings.sp1_label || 'Type 1';
    const sp2Label = settings.sp2_label || 'Type 2';
    const sp3Label = settings.sp3_label || 'Type 3';

    if (custType === 'Type 1' || custType === sp1Label) return item.sp1 || item.selling_price;
    if (custType === 'Type 2' || custType === sp2Label) return item.sp2 || item.selling_price;
    if (custType === 'Type 3' || custType === sp3Label) return item.sp3 || item.selling_price;
    return item.selling_price;
  };

  const handleItemChange = (index, itemId) => {
    const item = items.find(it => it.id === parseInt(itemId));
    const customer = customers.find(c => c.id === parseInt(customerId));

    const sp1Label = settings.sp1_label || 'Type 1';
    const sp2Label = settings.sp2_label || 'Type 2';
    const sp3Label = settings.sp3_label || 'Type 3';
    
    let rateType = 'selling_price';
    if (customer) {
      const cType = customer.customer_type;
      if (cType === 'Type 1' || cType === sp1Label) rateType = 'sp1';
      else if (cType === 'Type 2' || cType === sp2Label) rateType = 'sp2';
      else if (cType === 'Type 3' || cType === sp3Label) rateType = 'sp3';
    }
    
    let rate = 0;
    if (item) {
      if (rateType === 'selling_price') rate = item.selling_price;
      else if (rateType === 'sp1') rate = item.sp1 || item.selling_price;
      else if (rateType === 'sp2') rate = item.sp2 || item.selling_price;
      else if (rateType === 'sp3') rate = item.sp3 || item.selling_price;
    }

    const updated = [...invoiceItems];
    updated[index] = { ...updated[index], item_id: itemId, rate_type: rateType, rate };
    setInvoiceItems(updated);
  };

  const handleRateTypeChange = (index, type) => {
    const updated = [...invoiceItems];
    const itemRow = updated[index];
    const item = items.find(it => it.id === parseInt(itemRow.item_id));
    let rate = 0;
    if (item) {
      if (type === 'selling_price') rate = item.selling_price;
      else if (type === 'sp1') rate = item.sp1 || item.selling_price;
      else if (type === 'sp2') rate = item.sp2 || item.selling_price;
      else if (type === 'sp3') rate = item.sp3 || item.selling_price;
    }
    updated[index] = { ...itemRow, rate_type: type, rate };
    setInvoiceItems(updated);
  };

  const handleRowChange = (index, field, value) => {
    const updated = [...invoiceItems];
    updated[index] = { ...updated[index], [field]: value };
    setInvoiceItems(updated);
  };

  const addRow = () => {
    setInvoiceItems([...invoiceItems, { item_id: '', quantity: 1, rate_type: 'selling_price', rate: 0, discount_percent: 0 }]);
  };

  const removeRow = (idx) => {
    setInvoiceItems(invoiceItems.filter((_, i) => i !== idx));
  };

  const handleOpenCreate = () => {
    setEditingInvoiceId(null);
    setCustomerId('');
    setInvDate(new Date().toISOString().split('T')[0]);
    setDueDate('');
    setSalesperson('');
    setOrderNumber('');
    setTerms('');
    setSubject('');
    setNotes('');
    setCustomerNotes('');
    setTermsConditions('');
    setTdsAmount(0);
    setTcsAmount(0);
    setAdjustment(0);
    setRoundOff(0);
    setStatus('Sent');
    setInvoiceItems([{ item_id: '', quantity: 1, rate: 0, discount_percent: 0 }]);
    setShowCreate(true);
  };

  const handleEditInvoice = async (invoiceId) => {
    try {
      const res = await fetch(`${API_BASE}/invoices/${invoiceId}`, { headers: getHeaders() });
      if (res.ok) {
        const data = await res.json();
        const inv = data.invoice;
        setEditingInvoiceId(inv.id);
        setCustomerId(inv.customer_id.toString());
        setInvDate(inv.date ? inv.date.split('T')[0] : '');
        setDueDate(inv.due_date ? inv.due_date.split('T')[0] : '');
        setSalesperson(inv.salesperson || '');
        setOrderNumber(inv.order_number || '');
        setSelectedOutlet(inv.outlet_id || 1);
        setTerms(inv.terms || '');
        setSubject(inv.subject || '');
        setNotes(inv.notes || '');
        setCustomerNotes(inv.customer_notes || '');
        setTermsConditions(inv.terms_conditions || '');
        setTdsAmount(inv.tds_amount || 0);
        setTcsAmount(inv.tcs_amount || 0);
        setAdjustment(inv.adjustment || 0);
        setRoundOff(inv.round_off || 0);
        setStatus(inv.status || 'Sent');

        if (data.items && data.items.length > 0) {
          setInvoiceItems(data.items.map(it => ({
            item_id: it.item_id.toString(),
            quantity: it.quantity,
            rate_type: 'selling_price',
            rate: it.rate,
            discount_percent: it.discount_percent || 0
          })));
        } else {
          setInvoiceItems([{ item_id: '', quantity: 1, rate: 0, discount_percent: 0 }]);
        }
        setSelectedInvoice(null);
        setShowCreate(true);
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingInvoiceId ? `${API_BASE}/invoices/${editingInvoiceId}` : `${API_BASE}/invoices`;
      const method = editingInvoiceId ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method,
        headers: getHeaders(),
        body: JSON.stringify({
          customer_id: parseInt(customerId),
          date: invDate,
          due_date: dueDate,
          notes,
          salesperson,
          round_off: parseFloat(roundOff) || 0,
          outlet_id: parseInt(selectedOutlet) || 1,
          order_number: orderNumber,
          terms,
          subject,
          customer_notes: customerNotes,
          terms_conditions: termsConditions,
          tds_amount: parseFloat(tdsAmount) || 0,
          tcs_amount: parseFloat(tcsAmount) || 0,
          adjustment: parseFloat(adjustment) || 0,
          status,
          items: invoiceItems.map(ii => ({
            item_id: parseInt(ii.item_id),
            quantity: parseFloat(ii.quantity),
            rate: parseFloat(ii.rate),
            discount_percent: parseFloat(ii.discount_percent || 0)
          }))
        })
      });
      if (res.ok) {
        setShowCreate(false);
        setEditingInvoiceId(null);
        reload();
      } else {
        const err = await res.json();
        alert(err.error || 'Failed to save invoice');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const viewInvoiceDetail = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/invoices/${id}`, { headers: getHeaders() });
      if (res.ok) {
        const data = await res.json();
        setSelectedInvoice(data);
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleMarkInvoiceSent = async (invoiceId) => {
    if (!confirm('Mark this draft invoice as Sent?')) return;
    try {
      const res = await fetch(`${API_BASE}/invoices/${invoiceId}/status`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify({ status: 'Sent' })
      });
      if (res.ok) {
        reload();
      } else {
        const err = await res.json();
        alert(err.error || 'Failed to update invoice status');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteInvoice = async (invoiceId) => {
    if (!confirm('Are you sure you want to delete this invoice? This will restore stock levels.')) return;
    try {
      const res = await fetch(`${API_BASE}/invoices/${invoiceId}`, {
        method: 'DELETE',
        headers: getHeaders()
      });
      if (res.ok) {
        reload();
      } else {
        const err = await res.json();
        alert(err.error || 'Failed to delete invoice');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleExportInvoices = () => {
    const headers = ['Invoice Number', 'Customer Name', 'Date', 'Due Date', 'Subtotal', 'Tax Amount', 'Grand Total', 'Status'];
    const mapping = ['invoice_number', 'customer_name', 'date', 'due_date', 'subtotal', 'tax_amount', 'grand_total', 'status'];
    exportToCSV(invoices, headers, mapping, 'sales_invoices');
  };

  return (
    <div>
      {!showCreate && !selectedInvoice && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
            <div>
              <h1 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>Sales Invoices</h1>
              <p style={{ color: 'var(--text-secondary)' }}>Create B2B / B2C GST-Compliant sales receipts.</p>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={handleExportInvoices} className="btn btn-secondary" style={{ border: '1px solid var(--border-color)' }}>
                <Download size={18} />
                <span>Export CSV</span>
              </button>
              <button onClick={handleOpenCreate} className="btn btn-primary">
                <Plus size={18} />
                <span>Create Invoice</span>
              </button>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Invoice Number</th>
                  <th>Customer Name</th>
                  <th>Date</th>
                  <th>Due Date</th>
                  <th>Subtotal</th>
                  <th>Tax Amount</th>
                  <th>Grand Total</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map(inv => {
                  const effStatus = getInvoiceStatus(inv);
                  return (
                    <tr key={inv.id}>
                      <td><strong>{inv.invoice_number}</strong></td>
                      <td>{inv.customer_name}</td>
                      <td>{new Date(inv.date).toLocaleDateString()}</td>
                      <td>{inv.due_date ? new Date(inv.due_date).toLocaleDateString() : '-'}</td>
                      <td>₹{inv.subtotal.toFixed(2)}</td>
                      <td>₹{inv.tax_amount.toFixed(2)}</td>
                      <td>₹{inv.grand_total.toFixed(2)}</td>
                      <td>
                        <span style={{
                          padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: '600',
                          background: effStatus === 'Paid' ? 'var(--success-bg)' 
                                    : effStatus === 'Partially Paid' ? 'var(--warning-bg)' 
                                    : effStatus === 'Overdue' ? 'var(--danger-bg)'
                                    : effStatus === 'Draft' ? 'var(--bg-tertiary)'
                                    : 'rgba(59, 130, 246, 0.15)',
                          color: effStatus === 'Paid' ? 'var(--success)' 
                               : effStatus === 'Partially Paid' ? 'var(--warning)' 
                               : effStatus === 'Overdue' ? 'var(--danger)'
                               : effStatus === 'Draft' ? 'var(--text-secondary)'
                               : '#3b82f6'
                        }}>
                          {effStatus}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button onClick={() => viewInvoiceDetail(inv.id)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>View Detail</button>
                          {user?.role === 'Admin' && (
                            <button onClick={() => handleEditInvoice(inv.id)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem', color: 'var(--accent-primary)', border: '1px solid var(--border-color)' }}>
                              <Edit size={14} />
                              <span>Edit</span>
                            </button>
                          )}
                          {inv.status === 'Draft' && (
                            <button onClick={() => handleMarkInvoiceSent(inv.id)} className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '0.8rem', background: 'rgba(59, 130, 246, 0.15)', color: '#3b82f6', border: '1px solid rgba(59, 130, 246, 0.3)', boxShadow: 'none' }}>
                              <Send size={13} />
                              <span>Mark Sent</span>
                            </button>
                          )}
                          <button onClick={() => handleDeleteInvoice(inv.id)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: '0.8rem', background: 'var(--danger-bg)', color: 'var(--danger)', border: '1px solid rgba(239,68,68,0.3)', boxShadow: 'none' }}>
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}

      {showCreate && (
        <div className="card">
          <h2 style={{ marginBottom: '24px' }}>{editingInvoiceId ? 'Edit Sales Invoice' : 'New Sales Invoice'}</h2>
          <form onSubmit={handleCreateSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
              <div className="form-group">
                <label className="form-label">Customer</label>
                <select className="form-control" value={customerId} onChange={e => handleCustomerChange(e.target.value)} required>
                  <option value="">Select Customer</option>
                  {customers.map(c => <option key={c.id} value={c.id}>{c.name} - {c.customer_type} ({c.state})</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Salesperson</label>
                <input className="form-control" type="text" value={salesperson} onChange={e => setSalesperson(e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Order Number</label>
                <input className="form-control" type="text" value={orderNumber} onChange={e => setOrderNumber(e.target.value)} placeholder="Order Ref" />
              </div>
              <div className="form-group">
                <label className="form-label">Assigned Outlet</label>
                {user?.role === 'Admin' ? (
                  <select className="form-control" value={selectedOutlet} onChange={e => handleOutletChange(e.target.value)}>
                    {outlets.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}
                  </select>
                ) : (
                  <input className="form-control" type="text" readOnly value={outlets.find(o => o.id === user?.outlet_id)?.name || 'Main Outlet'} />
                )}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1.5fr 1fr', gap: '20px', marginBottom: '20px' }}>
              <div className="form-group">
                <label className="form-label">Invoice Date</label>
                <input className="form-control" type="date" value={invDate} onChange={e => setInvDate(e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">Due Date</label>
                <input className="form-control" type="date" value={dueDate} onChange={e => setDueDate(e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Payment Terms</label>
                <input className="form-control" type="text" value={terms} onChange={e => setTerms(e.target.value)} placeholder="Net 30, Due on Receipt" />
                <div style={{ marginTop: '6px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {[
                    { label: 'Receipt', days: 0 },
                    { label: 'Net 15', days: 15 },
                    { label: 'Net 30', days: 30 },
                    { label: 'Net 45', days: 45 },
                    { label: 'Net 60', days: 60 }
                  ].map(p => (
                    <button
                      key={p.days}
                      type="button"
                      onClick={() => applyTermsPreset(p.days, p.days === 0 ? 'Due on Receipt' : p.label)}
                      className="btn btn-secondary"
                      style={{
                        padding: '2px 8px',
                        fontSize: '0.73rem',
                        borderRadius: '12px',
                        border: '1px solid var(--border-color)',
                        background: (terms === p.label || (p.days === 0 && terms === 'Due on Receipt')) ? 'var(--accent-primary)' : 'var(--bg-secondary)',
                        color: (terms === p.label || (p.days === 0 && terms === 'Due on Receipt')) ? '#ffffff' : 'var(--text-secondary)'
                      }}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Subject</label>
                <input className="form-control" type="text" value={subject} onChange={e => setSubject(e.target.value)} placeholder="Subject" />
              </div>
            </div>

            <h4 style={{ marginBottom: '12px' }}>Line Items</h4>
            {invoiceItems.map((row, idx) => (
              <div key={idx} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1.2fr 1fr 1fr auto', gap: '12px', alignItems: 'center', marginBottom: '12px' }}>
                <select className="form-control" value={row.item_id} onChange={e => handleItemChange(idx, e.target.value)} required>
                  <option value="">Select Item</option>
                  {items.filter(it => it.is_sellable === undefined || it.is_sellable === 1 || it.is_sellable === true).map(it => (
                    <option key={it.id} value={it.id}>{it.name} - SKU: {it.sku} (Qty: {it.stock_on_hand})</option>
                  ))}
                </select>
                <input className="form-control" type="number" min="0.1" step="any" placeholder="Qty" value={row.quantity} onChange={e => handleRowChange(idx, 'quantity', e.target.value)} required />
                <select className="form-control" value={row.rate_type || 'selling_price'} onChange={e => handleRateTypeChange(idx, e.target.value)}>
                  <option value="selling_price">Base SP</option>
                  <option value="sp1">SP1 ({settings.sp1_label || 'Tier 1'})</option>
                  <option value="sp2">SP2 ({settings.sp2_label || 'Tier 2'})</option>
                  <option value="sp3">SP3 ({settings.sp3_label || 'Tier 3'})</option>
                </select>
                <input className="form-control" type="number" step="any" placeholder="Rate" value={row.rate} onChange={e => handleRowChange(idx, 'rate', e.target.value)} required />
                <input className="form-control" type="number" step="any" placeholder="Disc %" value={row.discount_percent} onChange={e => handleRowChange(idx, 'discount_percent', e.target.value)} />
                <button type="button" onClick={() => removeRow(idx)} className="btn btn-danger" style={{ padding: '10px' }}>X</button>
              </div>
            ))}

            <button type="button" onClick={addRow} className="btn btn-secondary" style={{ marginBottom: '24px' }}>
              <Plus size={16} />
              <span>Add Item Line</span>
            </button>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
              <div className="form-group">
                <label className="form-label">Notes (Internal)</label>
                <textarea className="form-control" rows="2" value={notes} onChange={e => setNotes(e.target.value)}></textarea>
              </div>
              <div className="form-group">
                <label className="form-label">Customer Notes (Shown on Bill)</label>
                <textarea className="form-control" rows="2" value={customerNotes} onChange={e => setCustomerNotes(e.target.value)} placeholder="Thanks for your business."></textarea>
              </div>
              <div className="form-group">
                <label className="form-label">Terms & Conditions</label>
                <textarea className="form-control" rows="2" value={termsConditions} onChange={e => setTermsConditions(e.target.value)} placeholder="Enter terms & conditions..."></textarea>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr 1fr', gap: '16px', alignItems: 'center', marginBottom: '20px' }}>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">TDS Deducted (- ₹)</label>
                <input className="form-control" type="number" step="any" value={tdsAmount} onChange={e => setTdsAmount(e.target.value)} placeholder="0.00" style={{ marginBottom: 0 }} />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">TCS Collected (+ ₹)</label>
                <input className="form-control" type="number" step="any" value={tcsAmount} onChange={e => setTcsAmount(e.target.value)} placeholder="0.00" style={{ marginBottom: 0 }} />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Adjustment (+/- ₹)</label>
                <input className="form-control" type="number" step="any" value={adjustment} onChange={e => setAdjustment(e.target.value)} placeholder="0.00" style={{ marginBottom: 0 }} />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Round-Off (₹)</label>
                <input className="form-control" type="number" step="any" value={roundOff} onChange={e => setRoundOff(e.target.value)} placeholder="0.00" style={{ marginBottom: 0 }} />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Save Status</label>
                <select className="form-control" value={status} onChange={e => setStatus(e.target.value)} style={{ marginBottom: 0 }}>
                  <option value="Sent">Sent (Active)</option>
                  <option value="Draft">Draft</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '30px' }}>
              <button type="button" onClick={() => { setShowCreate(false); setEditingInvoiceId(null); }} className="btn btn-secondary">Cancel</button>
              <button type="submit" className="btn btn-primary">{editingInvoiceId ? 'Update Invoice' : 'Save Invoice'}</button>
            </div>
          </form>
        </div>
      )}

      {selectedInvoice && (
        <div>
          {/* Layout Switcher (No Print on print mode) */}
          <div className="no-print" style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '24px', background: 'var(--bg-secondary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>Select Print Template:</span>
            {['a4', 'a5', 'thermal'].map(lay => (
              <button 
                key={lay} 
                onClick={() => setPrintLayout(lay)} 
                className={`bi-chart-tab${printLayout === lay ? ' active' : ''}`}
                style={{ textTransform: 'uppercase' }}
              >
                {lay === 'thermal' ? 'Thermal 80mm' : lay}
              </button>
            ))}
            <div style={{ marginLeft: 'auto', display: 'flex', gap: '10px' }}>
              <button onClick={() => window.print()} className="btn btn-primary" style={{ padding: '8px 16px' }}>Print / Save PDF</button>
              <button onClick={() => setSelectedInvoice(null)} className="btn btn-secondary" style={{ padding: '8px 16px' }}>Back to List</button>
            </div>
          </div>

          {/* Render layout-specific wrapper */}
          <div className={`print-area ${printLayout === 'a4' ? 'preview-a4' : printLayout === 'a5' ? 'preview-a5' : 'preview-thermal'}`}>
            {printLayout === 'thermal' ? (
              <div style={{ fontFamily: 'Courier New, monospace', fontSize: '0.8rem', color: '#000', width: '100%', maxWidth: '320px', margin: '0 auto', background: '#fff', padding: '12px 8px' }}>
                <div style={{ textAlign: 'center', fontWeight: 'bold', fontSize: '1.05rem', marginBottom: '8px' }}>
                  {settings.company_name || 'My Shop'}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                  <span>GST: {selectedInvoice.invoice.outlet_gstin || settings.company_gstin || ''}</span>
                  <span>Mob: {selectedInvoice.invoice.outlet_phone || settings.company_phone || ''}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '4px' }}>
                  <span>Bill No: <strong>{selectedInvoice.invoice.invoice_number}</strong></span>
                  <span>Date: {new Date(selectedInvoice.invoice.date).toLocaleDateString()}</span>
                </div>

                {(selectedInvoice.invoice.outlet_address || settings.company_address) && (
                  <div style={{ fontSize: '0.75rem', marginBottom: '8px' }}>
                    Address: {(selectedInvoice.invoice.outlet_address || settings.company_address || '').replace(/\n/g, ', ')}
                  </div>
                )}

                <div style={{ margin: '4px 0 2px' }}>item ------------------------------------</div>

                <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1.5fr 1.5fr', fontWeight: 'bold', fontSize: '0.78rem' }}>
                  <div>sl.no</div>
                  <div style={{ textAlign: 'center' }}>Qty</div>
                  <div style={{ textAlign: 'right' }}>rate</div>
                  <div style={{ textAlign: 'right' }}>amount</div>
                </div>

                <div style={{ margin: '2px 0 6px', overflow: 'hidden', whiteSpace: 'nowrap' }}>_____________________________________</div>

                {selectedInvoice.items.map((ii, idx) => (
                  <div key={ii.id || idx} style={{ marginBottom: '6px' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '0.78rem', wordBreak: 'break-word' }}>
                      {idx + 1}. {ii.item_name}
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1.5fr 1.5fr', fontSize: '0.78rem' }}>
                      <div></div>
                      <div style={{ textAlign: 'center' }}>{ii.quantity}</div>
                      <div style={{ textAlign: 'right' }}>₹{ii.rate.toFixed(2)}</div>
                      <div style={{ textAlign: 'right' }}>₹{ii.amount.toFixed(2)}</div>
                    </div>
                    <div style={{ borderBottom: '1px dashed #444', margin: '4px 0' }}></div>
                  </div>
                ))}

                {(() => {
                  const totalQty = selectedInvoice.items.reduce((acc, curr) => acc + (curr.quantity || 1), 0);
                  const totalRate = selectedInvoice.items.reduce((acc, curr) => acc + (curr.rate || 0), 0);
                  return (
                    <>
                      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1.5fr 1.5fr', fontWeight: 'bold', borderTop: '1px solid #000', borderBottom: '1px solid #000', padding: '4px 0', fontSize: '0.78rem' }}>
                        <div>total</div>
                        <div style={{ textAlign: 'center' }}>{totalQty}</div>
                        <div style={{ textAlign: 'right' }}>₹{totalRate.toFixed(2)}</div>
                        <div style={{ textAlign: 'right' }}>₹{selectedInvoice.invoice.subtotal.toFixed(2)}</div>
                      </div>

                      <div style={{ textAlign: 'right', marginTop: '8px', fontWeight: 'bold', fontSize: '0.78rem' }}>
                        gst applicable = ₹{selectedInvoice.invoice.tax_amount.toFixed(2)}
                      </div>
                      <div style={{ textAlign: 'right', marginTop: '2px', fontWeight: 'bold', fontSize: '0.85rem' }}>
                        payable = ₹{selectedInvoice.invoice.grand_total.toFixed(2)}
                      </div>
                    </>
                  );
                })()}

                <div style={{ textAlign: 'center', marginTop: '16px', borderTop: '1px dashed #444', paddingTop: '8px', fontSize: '0.75rem' }}>
                  <p style={{ margin: 0 }}>Thank you for shopping with us!</p>
                  <p style={{ margin: '2px 0 0', opacity: 0.7 }}>Powered by TSL SwiftBill ERP POS</p>
                </div>
              </div>
            ) : (
              <>
                {/* Header info */}
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #ddd', paddingBottom: '16px', marginBottom: '16px' }}>
                  <div>
                    {(selectedInvoice.invoice.outlet_logo_url || settings.company_logo) ? (
                      <img src={selectedInvoice.invoice.outlet_logo_url || settings.company_logo} alt="Logo" style={{ maxHeight: '40px', marginBottom: '8px', objectFit: 'contain' }} onError={e => e.target.style.display = 'none'} />
                    ) : (
                      <div style={{
                        padding: '6px 12px',
                        background: 'rgba(99, 102, 241, 0.1)',
                        color: 'var(--accent-primary)',
                        fontWeight: '800',
                        fontSize: '1.1rem',
                        borderRadius: '4px',
                        display: 'inline-block',
                        marginBottom: '10px',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        borderLeft: '4px solid var(--accent-primary)',
                        fontFamily: 'var(--font-family-display)'
                      }}>
                        {settings.company_name || 'LEDGERPRO'}
                      </div>
                    )}
                    <h2 style={{ fontSize: '1.5rem', margin: 0 }}>TAX INVOICE</h2>
                    <p style={{ margin: '2px 0 0', fontSize: '0.85rem' }}>Inv #: <strong>{selectedInvoice.invoice.invoice_number}</strong></p>
                    <p style={{ margin: '2px 0 0', fontSize: '0.85rem' }}>Date: {new Date(selectedInvoice.invoice.date).toLocaleDateString()}</p>
                    {selectedInvoice.invoice.due_date && <p style={{ margin: '2px 0 0', fontSize: '0.85rem' }}>Due Date: {new Date(selectedInvoice.invoice.due_date).toLocaleDateString()}</p>}
                    <p style={{ margin: '2px 0 0', fontSize: '0.85rem' }}>Outlet: {selectedInvoice.invoice.outlet_name || 'Main Outlet'}</p>
                  </div>
                  
                  <div style={{ textAlign: 'right' }}>
                    <h3 style={{ margin: 0, fontSize: '1.2rem' }}>{settings.company_name || 'My Company'}</h3>
                    <p style={{ fontSize: '0.8rem', margin: '4px 0 0', whiteSpace: 'pre-line' }}>{selectedInvoice.invoice.outlet_address || settings.company_address || ''}</p>
                    <p style={{ fontSize: '0.8rem', margin: '2px 0 0' }}>GSTIN: {selectedInvoice.invoice.outlet_gstin || settings.company_gstin || ''}</p>
                    {(selectedInvoice.invoice.outlet_phone || selectedInvoice.invoice.outlet_email) && (
                      <p style={{ fontSize: '0.78rem', margin: '2px 0 0' }}>
                        {[selectedInvoice.invoice.outlet_phone, selectedInvoice.invoice.outlet_email].filter(Boolean).join(' | ')}
                      </p>
                    )}
                  </div>
                </div>

                {/* Billed To */}
                <div style={{ marginBottom: '16px', fontSize: '0.85rem' }}>
                  <p style={{ fontWeight: 'bold', margin: '0 0 4px' }}>Billed To:</p>
                  <p style={{ margin: 0 }}><strong>{selectedInvoice.invoice.customer_name}</strong></p>
                  <p style={{ margin: 0 }}>{selectedInvoice.invoice.customer_address || ''}</p>
                  <p style={{ margin: 0 }}>State: {selectedInvoice.invoice.customer_state || ''}</p>
                  <p style={{ margin: 0 }}>GSTIN: {selectedInvoice.invoice.customer_gstin || ''}</p>
                </div>

                {/* Items Table */}
                <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '16px', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #000' }}>
                      <th style={{ textAlign: 'left', padding: '6px 4px' }}>Item Details</th>
                      <th style={{ textAlign: 'center', padding: '6px 4px' }}>Qty</th>
                      <th style={{ textAlign: 'right', padding: '6px 4px' }}>Rate</th>
                      <th style={{ textAlign: 'right', padding: '6px 4px' }}>Disc %</th>
                      <th style={{ textAlign: 'right', padding: '6px 4px' }}>GST %</th>
                      <th style={{ textAlign: 'right', padding: '6px 4px' }}>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedInvoice.items.map(ii => (
                      <tr key={ii.id} style={{ borderBottom: '1px solid #eee' }}>
                        <td style={{ padding: '6px 4px' }}>
                          <strong>{ii.item_name}</strong>
                          <span style={{ fontSize: '0.75rem', display: 'block', opacity: 0.8 }}>SKU: {ii.item_sku} | HSN: {ii.item_hsn}</span>
                        </td>
                        <td style={{ textAlign: 'center', padding: '6px 4px' }}>{ii.quantity}</td>
                        <td style={{ textAlign: 'right', padding: '6px 4px' }}>₹{ii.rate.toFixed(2)}</td>
                        <td style={{ textAlign: 'right', padding: '6px 4px' }}>{ii.discount_percent}%</td>
                        <td style={{ textAlign: 'right', padding: '6px 4px' }}>{ii.gst_percent}%</td>
                        <td style={{ textAlign: 'right', padding: '6px 4px' }}>₹{ii.amount.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Bottom calculation and UPI QR code */}
                <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #eee', paddingTop: '16px', flexWrap: 'wrap', gap: '16px' }}>
                  {/* Left side: UPI payment QR Code */}
                  <div>
                    {(selectedInvoice.invoice.outlet_upi_id || settings.company_upi_id) ? (() => {
                      const upiId = selectedInvoice.invoice.outlet_upi_id || settings.company_upi_id;
                      const upiUri = `upi://pay?pa=${upiId}&pn=${encodeURIComponent(settings.company_name || 'LedgerPro')}&am=${selectedInvoice.invoice.grand_total.toFixed(2)}&cu=INR&tn=Invoice-${selectedInvoice.invoice.invoice_number}`;
                      const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=${encodeURIComponent(upiUri)}`;
                      return (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', border: '1px solid #ddd', padding: '8px', borderRadius: '6px', maxWidth: '280px', background: 'var(--bg-secondary)' }}>
                          <img src={qrUrl} alt="UPI QR Code" style={{ width: '80px', height: '80px' }} />
                          <div style={{ fontSize: '0.75rem' }}>
                            <p style={{ fontWeight: 'bold', margin: '0 0 2px' }}>Scan & Pay via UPI</p>
                            <p style={{ margin: '0 0 2px', wordBreak: 'break-all', opacity: 0.8 }}>{upiId}</p>
                            <p style={{ margin: 0, fontWeight: 'bold' }}>Amount: ₹{selectedInvoice.invoice.grand_total.toFixed(2)}</p>
                          </div>
                        </div>
                      );
                    })() : (
                      <div style={{ fontSize: '0.75rem', color: '#999' }}>No UPI ID configured.</div>
                    )}
                  </div>

                  {/* Right side: Calculations */}
                  <div style={{ width: '220px', display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.85rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Subtotal:</span>
                      <span>₹{selectedInvoice.invoice.subtotal.toFixed(2)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>GST Tax:</span>
                      <span>₹{selectedInvoice.invoice.tax_amount.toFixed(2)}</span>
                    </div>
                    {selectedInvoice.invoice.round_off !== 0 && (
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Round-off:</span>
                        <span>₹{selectedInvoice.invoice.round_off.toFixed(2)}</span>
                      </div>
                    )}
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', borderTop: '1px solid #000', paddingTop: '6px', fontSize: '0.95rem' }}>
                      <span>Grand Total:</span>
                      <span>₹{selectedInvoice.invoice.grand_total.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                {/* Receipt Footer */}
                <div style={{ textAlign: 'center', marginTop: '24px', fontSize: '0.78rem', borderTop: '1px dashed #ddd', paddingTop: '10px' }}>
                  <p style={{ margin: 0 }}>Thank you for shopping with us!</p>
                  <p style={{ margin: '2px 0 0', opacity: 0.7 }}>Powered by TSL SwiftBill ERP</p>
                </div>
              </>
            )}
          </div>

          <div className="no-print" style={{ marginTop: '20px', display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <button onClick={() => setSelectedInvoice(null)} className="btn btn-secondary">Close Invoice Preview</button>
          </div>
        </div>
      )}
    </div>
  );
}

// ==================== VIEW: BILLS ====================
function BillsView({ bills, vendors, items, getHeaders, reload, settings }) {
  const [showCreate, setShowCreate] = useState(false);
  const [selectedBill, setSelectedBill] = useState(null);
  const [printLayout, setPrintLayout] = useState('a4'); // 'a4' | 'a5' | 'thermal'

  // Form Fields
  const [billNumber, setBillNumber] = useState('');
  const [vendorId, setVendorId] = useState('');
  const [billDate, setBillDate] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [notes, setNotes] = useState('');
  const [billItems, setBillItems] = useState([{ item_id: '', quantity: 1, rate: 0 }]);
  const [orderNumber, setOrderNumber] = useState('');
  const [paymentTerms, setPaymentTerms] = useState('');
  const [reverseCharge, setReverseCharge] = useState(false);
  const [adjustment, setAdjustment] = useState(0);
  const [tdsAmount, setTdsAmount] = useState(0);
  const [tcsAmount, setTcsAmount] = useState(0);
  const [discountAmount, setDiscountAmount] = useState(0);
  const [status, setStatus] = useState('Due');

  const handleItemChange = (index, itemId) => {
    const item = items.find(it => it.id === parseInt(itemId));
    const updated = [...billItems];
    updated[index] = { ...updated[index], item_id: itemId, rate: item?.purchase_price || 0 };
    setBillItems(updated);
  };

  const handleRowChange = (index, field, value) => {
    const updated = [...billItems];
    updated[index] = { ...updated[index], [field]: value };
    setBillItems(updated);
  };

  const addRow = () => {
    setBillItems([...billItems, { item_id: '', quantity: 1, rate: 0 }]);
  };

  const removeRow = (idx) => {
    setBillItems(billItems.filter((_, i) => i !== idx));
  };

  const viewBillDetail = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/bills/${id}`, { headers: getHeaders() });
      if (res.ok) {
        const data = await res.json();
        setSelectedBill(data);
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleMarkAsPaid = async (bill) => {
    if (!window.confirm(`Mark Bill ${bill.bill_number} as fully paid?`)) return;
    try {
      const res = await fetch(`${API_BASE}/payments`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          vendor_id: bill.vendor_id,
          amount: parseFloat(bill.balance_due),
          date: new Date().toISOString().substring(0, 10),
          method: 'Bank Transfer',
          notes: `Quick paid from Bills log`,
          payment_number: `PAY-BILL-${Date.now()}`,
          allocations: [{
            bill_id: bill.id,
            amount: parseFloat(bill.balance_due)
          }]
        })
      });
      if (res.ok) {
        reload();
      } else {
        const err = await res.json();
        alert(err.error || 'Failed to mark as paid');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleMarkBillDue = async (billId) => {
    if (!confirm('Mark this draft bill as Due/Unpaid?')) return;
    try {
      const res = await fetch(`${API_BASE}/bills/${billId}/status`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify({ status: 'Due' })
      });
      if (res.ok) {
        reload();
      } else {
        const err = await res.json();
        alert(err.error || 'Failed to update bill status');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteBill = async (billId) => {
    if (!confirm('Are you sure you want to delete this purchase bill? This will reduce stock levels.')) return;
    try {
      const res = await fetch(`${API_BASE}/bills/${billId}`, {
        method: 'DELETE',
        headers: getHeaders()
      });
      if (res.ok) {
        reload();
      } else {
        const err = await res.json();
        alert(err.error || 'Failed to delete bill');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/bills`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          bill_number: billNumber,
          vendor_id: parseInt(vendorId),
          date: billDate,
          due_date: dueDate,
          notes,
          order_number: orderNumber,
          payment_terms: paymentTerms,
          reverse_charge: reverseCharge ? 1 : 0,
          adjustment: parseFloat(adjustment) || 0,
          tds_amount: parseFloat(tdsAmount) || 0,
          tcs_amount: parseFloat(tcsAmount) || 0,
          discount_amount: parseFloat(discountAmount) || 0,
          status,
          items: billItems.map(ii => ({
            item_id: parseInt(ii.item_id),
            quantity: parseFloat(ii.quantity),
            rate: parseFloat(ii.rate)
          }))
        })
      });
      if (res.ok) {
        setShowCreate(false);
        reload();
      } else {
        const err = await res.json();
        alert(err.error || 'Failed to record bill');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleExportBills = () => {
    const headers = ['Bill Number', 'Vendor Name', 'Date', 'Due Date', 'Subtotal', 'Tax Amount', 'Grand Total', 'Status'];
    const mapping = ['bill_number', 'vendor_name', 'date', 'due_date', 'subtotal', 'tax_amount', 'grand_total', 'status'];
    exportToCSV(bills, headers, mapping, 'purchase_bills');
  };

  return (
    <div>
      {!showCreate && !selectedBill && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
            <div>
              <h1 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>Purchase Bills</h1>
              <p style={{ color: 'var(--text-secondary)' }}>Record incoming inventory invoices from suppliers.</p>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={handleExportBills} className="btn btn-secondary" style={{ border: '1px solid var(--border-color)' }}>
                <Download size={18} />
                <span>Export CSV</span>
              </button>
              <button onClick={() => setShowCreate(true)} className="btn btn-primary">
                <Plus size={18} />
                <span>Record Bill</span>
              </button>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Bill Number</th>
                  <th>Vendor Name</th>
                  <th>Date</th>
                  <th>Due Date</th>
                  <th>Subtotal</th>
                  <th>Tax Amount</th>
                  <th>Grand Total</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {bills.map(b => (
                  <tr key={b.id}>
                    <td><strong>{b.bill_number}</strong></td>
                    <td>{b.vendor_name}</td>
                    <td>{new Date(b.date).toLocaleDateString()}</td>
                    <td>{b.due_date ? new Date(b.due_date).toLocaleDateString() : '-'}</td>
                    <td>₹{b.subtotal.toFixed(2)}</td>
                    <td>₹{b.tax_amount.toFixed(2)}</td>
                    <td>₹{b.grand_total.toFixed(2)}</td>
                    <td>
                      <span style={{
                        padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem',
                        background: b.status === 'Paid' ? 'var(--success-bg)' : b.status === 'Partially Paid' ? 'var(--warning-bg)' : 'var(--danger-bg)',
                        color: b.status === 'Paid' ? 'var(--success)' : b.status === 'Partially Paid' ? 'var(--warning)' : 'var(--danger)'
                      }}>
                        {b.status}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button onClick={() => viewBillDetail(b.id)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>View Detail</button>
                        {b.status === 'Draft' && (
                          <button onClick={() => handleMarkBillDue(b.id)} className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '0.8rem', background: 'var(--warning-bg)', color: 'var(--warning)', border: '1px solid rgba(245,158,11,0.3)', boxShadow: 'none' }}>
                            Mark Due
                          </button>
                        )}
                        {b.status !== 'Paid' && b.status !== 'Draft' && (
                          <button onClick={() => handleMarkAsPaid(b)} className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '0.8rem', background: 'var(--success-bg)', color: 'var(--success)', border: '1px solid rgba(16,185,129,0.3)', boxShadow: 'none' }}>
                            Mark Paid
                          </button>
                        )}
                        <button onClick={() => handleDeleteBill(b.id)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: '0.8rem', background: 'var(--danger-bg)', color: 'var(--danger)', border: '1px solid rgba(239,68,68,0.3)', boxShadow: 'none' }}>
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {showCreate && (
        <div className="card">
          <h2 style={{ marginBottom: '24px' }}>Record Purchase Bill</h2>
          <form onSubmit={handleCreateSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
              <div className="form-group">
                <label className="form-label">Bill Number</label>
                <input className="form-control" type="text" value={billNumber} onChange={e => setBillNumber(e.target.value)} required placeholder="e.g. BILL-9921" />
              </div>
              <div className="form-group">
                <label className="form-label">Vendor</label>
                <select className="form-control" value={vendorId} onChange={e => setVendorId(e.target.value)} required>
                  <option value="">Select Vendor</option>
                  {vendors.map(v => <option key={v.id} value={v.id}>{v.name} ({v.state})</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Order Number</label>
                <input className="form-control" type="text" value={orderNumber} onChange={e => setOrderNumber(e.target.value)} placeholder="Order Ref" />
              </div>
              <div className="form-group">
                <label className="form-label">Payment Terms</label>
                <input className="form-control" type="text" value={paymentTerms} onChange={e => setPaymentTerms(e.target.value)} placeholder="e.g. Net 30" />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px', alignItems: 'center' }}>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Bill Date</label>
                <input className="form-control" type="date" value={billDate} onChange={e => setBillDate(e.target.value)} required style={{ marginBottom: 0 }} />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Due Date</label>
                <input className="form-control" type="date" value={dueDate} onChange={e => setDueDate(e.target.value)} style={{ marginBottom: 0 }} />
              </div>
              <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 0, marginTop: '22px' }}>
                <input type="checkbox" checked={reverseCharge} onChange={e => setReverseCharge(e.target.checked)} id="reverse_charge_checkbox" style={{ width: 'auto', cursor: 'pointer', margin: 0 }} />
                <label htmlFor="reverse_charge_checkbox" style={{ margin: 0, fontWeight: '600', cursor: 'pointer', fontSize: '0.9rem' }}>Subject to Reverse Charge</label>
              </div>
            </div>

            <h4 style={{ marginBottom: '12px' }}>Line Items</h4>
            {billItems.map((row, idx) => (
              <div key={idx} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr auto', gap: '12px', alignItems: 'center', marginBottom: '12px' }}>
                <select className="form-control" value={row.item_id} onChange={e => handleItemChange(idx, e.target.value)} required>
                  <option value="">Select Item</option>
                  {items.map(it => <option key={it.id} value={it.id}>{it.name} - SKU: {it.sku}</option>)}
                </select>
                <input className="form-control" type="number" min="0.1" step="any" placeholder="Qty" value={row.quantity} onChange={e => handleRowChange(idx, 'quantity', e.target.value)} required />
                <input className="form-control" type="number" step="any" placeholder="Purchase Cost" value={row.rate} onChange={e => handleRowChange(idx, 'rate', e.target.value)} required />
                <button type="button" onClick={() => removeRow(idx)} className="btn btn-danger" style={{ padding: '10px' }}>X</button>
              </div>
            ))}

            <button type="button" onClick={addRow} className="btn btn-secondary" style={{ marginBottom: '24px' }}>
              <Plus size={16} />
              <span>Add Item Line</span>
            </button>

            <div className="form-group">
              <label className="form-label">Notes</label>
              <textarea className="form-control" rows="2" value={notes} onChange={e => setNotes(e.target.value)} placeholder="Supplier notes..."></textarea>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr 1fr', gap: '16px', alignItems: 'center', marginBottom: '20px' }}>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">TDS Deducted (- ₹)</label>
                <input className="form-control" type="number" step="any" value={tdsAmount} onChange={e => setTdsAmount(e.target.value)} placeholder="0.00" style={{ marginBottom: 0 }} />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">TCS Collected (+ ₹)</label>
                <input className="form-control" type="number" step="any" value={tcsAmount} onChange={e => setTcsAmount(e.target.value)} placeholder="0.00" style={{ marginBottom: 0 }} />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Discount Amount (- ₹)</label>
                <input className="form-control" type="number" step="any" value={discountAmount} onChange={e => setDiscountAmount(e.target.value)} placeholder="0.00" style={{ marginBottom: 0 }} />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Adjustment (+/- ₹)</label>
                <input className="form-control" type="number" step="any" value={adjustment} onChange={e => setAdjustment(e.target.value)} placeholder="0.00" style={{ marginBottom: 0 }} />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Save Status</label>
                <select className="form-control" value={status} onChange={e => setStatus(e.target.value)} style={{ marginBottom: 0 }}>
                  <option value="Due">Unpaid (Due)</option>
                  <option value="Draft">Draft</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '30px' }}>
              <button type="button" onClick={() => setShowCreate(false)} className="btn btn-secondary">Cancel</button>
              <button type="submit" className="btn btn-primary">Save Bill</button>
            </div>
          </form>
        </div>
      )}

      {selectedBill && (
        <div>
          {/* Layout Switcher (No Print on print mode) */}
          <div className="no-print" style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '24px', background: 'var(--bg-secondary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>Select Print Template:</span>
            {['a4', 'a5', 'thermal'].map(lay => (
              <button 
                key={lay} 
                onClick={() => setPrintLayout(lay)} 
                className={`bi-chart-tab${printLayout === lay ? ' active' : ''}`}
                style={{ textTransform: 'uppercase' }}
              >
                {lay === 'thermal' ? 'Thermal 80mm' : lay}
              </button>
            ))}
            <div style={{ marginLeft: 'auto', display: 'flex', gap: '10px' }}>
              <button onClick={() => window.print()} className="btn btn-primary" style={{ padding: '8px 16px' }}>Print / Save PDF</button>
              <button onClick={() => setSelectedBill(null)} className="btn btn-secondary" style={{ padding: '8px 16px' }}>Back to List</button>
            </div>
          </div>

          {/* Render layout-specific wrapper */}
          <div className={`print-area ${printLayout === 'a4' ? 'preview-a4' : printLayout === 'a5' ? 'preview-a5' : 'preview-thermal'}`}>
            
            {/* Header info */}
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #000', paddingBottom: '16px', marginBottom: '16px' }}>
              <div>
                {(selectedBill.bill.outlet_logo_url || settings.company_logo) ? (
                  printLayout !== 'thermal' && (
                    <img src={selectedBill.bill.outlet_logo_url || settings.company_logo} alt="Logo" style={{ maxHeight: '40px', marginBottom: '8px', objectFit: 'contain' }} onError={e => e.target.style.display = 'none'} />
                  )
                ) : (
                  printLayout !== 'thermal' && (
                    <div style={{
                      padding: '6px 12px',
                      background: 'rgba(99, 102, 241, 0.1)',
                      color: 'var(--accent-primary)',
                      fontWeight: '800',
                      fontSize: '1.1rem',
                      borderRadius: '4px',
                      display: 'inline-block',
                      marginBottom: '10px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      borderLeft: '4px solid var(--accent-primary)',
                      fontFamily: 'var(--font-family-display)'
                    }}>
                      {settings.company_name || 'LEDGERPRO'}
                    </div>
                  )
                )}
                <h2 style={{ fontSize: printLayout === 'thermal' ? '1.1rem' : '1.5rem', margin: 0 }}>
                  {printLayout === 'thermal' ? 'PURCHASE RECEIPT' : 'PURCHASE BILL'}
                </h2>
                <p style={{ margin: '2px 0 0', fontSize: '0.85rem' }}>Bill #: <strong>{selectedBill.bill.bill_number}</strong></p>
                <p style={{ margin: '2px 0 0', fontSize: '0.85rem' }}>Date: {new Date(selectedBill.bill.date).toLocaleDateString()}</p>
                {selectedBill.bill.due_date && <p style={{ margin: '2px 0 0', fontSize: '0.85rem' }}>Due Date: {new Date(selectedBill.bill.due_date).toLocaleDateString()}</p>}
                <p style={{ margin: '2px 0 0', fontSize: '0.85rem' }}>Outlet: {selectedBill.bill.outlet_name || 'Main Outlet'}</p>
              </div>
              
              <div style={{ textAlign: 'right' }}>
                <h3 style={{ margin: 0, fontSize: printLayout === 'thermal' ? '1rem' : '1.2rem' }}>{selectedBill.bill.vendor_name}</h3>
                <p style={{ fontSize: '0.8rem', margin: '4px 0 0', whiteSpace: 'pre-line' }}>{selectedBill.bill.vendor_address || ''}</p>
                <p style={{ fontSize: '0.8rem', margin: '2px 0 0' }}>GSTIN: {selectedBill.bill.vendor_gstin || ''}</p>
                {(selectedBill.bill.vendor_phone || selectedBill.bill.vendor_email) && (
                  <p style={{ fontSize: '0.78rem', margin: '2px 0 0' }}>
                    {[selectedBill.bill.vendor_phone, selectedBill.bill.vendor_email].filter(Boolean).join(' | ')}
                  </p>
                )}
              </div>
            </div>

            {/* Billing To Company */}
            <div style={{ marginBottom: '16px', fontSize: '0.85rem' }}>
              <p style={{ fontWeight: 'bold', margin: '0 0 4px' }}>Billed To / Delivered To:</p>
              <p style={{ margin: 0 }}><strong>{settings.company_name || 'My Company'}</strong></p>
              <p style={{ margin: 0 }}>{selectedBill.bill.outlet_address || settings.company_address || ''}</p>
              <p style={{ margin: 0 }}>State: {selectedBill.bill.outlet_state || settings.company_state || ''}</p>
              <p style={{ margin: 0 }}>GSTIN: {selectedBill.bill.outlet_gstin || settings.company_gstin || ''}</p>
            </div>

            {/* Items Table */}
            <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '16px', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #000' }}>
                  <th style={{ textAlign: 'left', padding: '6px 4px' }}>Item Details</th>
                  <th style={{ textAlign: 'center', padding: '6px 4px' }}>Qty</th>
                  <th style={{ textAlign: 'right', padding: '6px 4px' }}>Rate</th>
                  <th style={{ textAlign: 'right', padding: '6px 4px' }}>Total</th>
                </tr>
              </thead>
              <tbody>
                {selectedBill.items.map(ii => (
                  <tr key={ii.id} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '6px 4px' }}>
                      <strong>{ii.item_name}</strong>
                      {printLayout !== 'thermal' && <span style={{ fontSize: '0.75rem', display: 'block', opacity: 0.8 }}>SKU: {ii.item_sku} | HSN: {ii.item_hsn}</span>}
                    </td>
                    <td style={{ textAlign: 'center', padding: '6px 4px' }}>{ii.quantity}</td>
                    <td style={{ textAlign: 'right', padding: '6px 4px' }}>₹{ii.rate.toFixed(2)}</td>
                    <td style={{ textAlign: 'right', padding: '6px 4px' }}>₹{ii.amount.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Bottom calculation */}
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #eee', paddingTop: '16px', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <p style={{ fontSize: '0.78rem', margin: 0, opacity: 0.8 }}>Notes: {selectedBill.bill.notes || 'No notes'}</p>
              </div>

              {/* Calculations */}
              <div style={{ width: '220px', display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.85rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Subtotal:</span>
                  <span>₹{selectedBill.bill.subtotal.toFixed(2)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>GST Tax:</span>
                  <span>₹{selectedBill.bill.tax_amount.toFixed(2)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', borderTop: '1px solid #000', paddingTop: '6px', fontSize: '0.95rem' }}>
                  <span>Grand Total:</span>
                  <span>₹{selectedBill.bill.grand_total.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Bill Footer */}
            <div style={{ textAlign: 'center', marginTop: '24px', fontSize: '0.78rem', borderTop: '1px dashed #ddd', paddingTop: '10px' }}>
              <p style={{ margin: 0 }}>Verified Inventory Receipt</p>
              <p style={{ margin: '2px 0 0', opacity: 0.7 }}>Powered by TSL SwiftBill ERP</p>
            </div>

          </div>

          <div className="no-print" style={{ marginTop: '20px', display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <button onClick={() => setSelectedBill(null)} className="btn btn-secondary">Close Bill Preview</button>
          </div>
        </div>
      )}
    </div>
  );
}

// ==================== VIEW: PAYMENTS ====================
function PaymentsView({ payments, invoices, bills, customers, vendors, getHeaders, reload }) {
  const [showForm, setShowForm] = useState(false);
  const [paymentDirection, setPaymentDirection] = useState('inbound'); // 'inbound' | 'outbound'
  
  // Left Column — Inbound (Customer)
  const [customerId, setCustomerId] = useState('');
  const [availableCredits, setAvailableCredits] = useState(0);
  const [useCredits, setUseCredits] = useState(true);
  const [amountReceived, setAmountReceived] = useState(0);
  const [bankCharges, setBankCharges] = useState(0);
  const [taxDeducted, setTaxDeducted] = useState(false);
  const [taxAccount, setTaxAccount] = useState('Yes, TDS (Income Tax)');
  const [taxAmount, setTaxAmount] = useState(0);

  // Outbound (Vendor) states
  const [vendorId, setVendorId] = useState('');
  const [unpaidBills, setUnpaidBills] = useState([]);
  const [billAllocations, setBillAllocations] = useState({});
  const [amountPaid, setAmountPaid] = useState(0);

  // Right Column
  const [payDate, setPayDate] = useState(new Date().toISOString().substring(0, 10));
  const [payNumber, setPayNumber] = useState(`PAY-${Date.now()}`);
  const [payMode, setPayMode] = useState('Bank Transfer');
  const [depositTo, setDepositTo] = useState('');
  const [reference, setReference] = useState('');

  // Unpaid invoices table rows
  const [unpaidList, setUnpaidList] = useState([]);
  const [allocations, setAllocations] = useState({}); // { invoiceId: amount }
  
  // Footer
  const [notes, setNotes] = useState('');
  const [sendThankYou, setSendThankYou] = useState(false);
  const [attachment, setAttachment] = useState(null);

  // Load unpaid invoices and credits when customer changes
  useEffect(() => {
    if (customerId) {
      loadCustomerDetails(customerId);
    } else {
      setUnpaidList([]);
      setAvailableCredits(0);
      setAllocations({});
    }
  }, [customerId]);

  const loadCustomerDetails = async (cId) => {
    try {
      const resInv = await fetch(`${API_BASE}/payments/unpaid-invoices/${cId}`, { headers: getHeaders() });
      if (resInv.ok) {
        const list = await resInv.json();
        setUnpaidList(list);
        const initialAllocs = {};
        list.forEach(i => initialAllocs[i.id] = 0);
        setAllocations(initialAllocs);
      }

      const resCredits = await fetch(`${API_BASE}/payments/credits/${cId}`, { headers: getHeaders() });
      if (resCredits.ok) {
        const data = await resCredits.json();
        setAvailableCredits(data.credits || 0.0);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Vendor Bills loading (Outbound)
  useEffect(() => {
    if (vendorId && paymentDirection === 'outbound') {
      loadVendorBills(vendorId);
    } else {
      setUnpaidBills([]);
      setBillAllocations({});
    }
  }, [vendorId, paymentDirection]);

  const loadVendorBills = async (vId) => {
    try {
      const res = await fetch(`${API_BASE}/payments/unpaid-bills/${vId}`, { headers: getHeaders() });
      if (res.ok) {
        const list = await res.json();
        setUnpaidBills(list);
        const initAllocs = {};
        list.forEach(b => initAllocs[b.id] = 0);
        setBillAllocations(initAllocs);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleAllocationChange = (invId, value) => {
    const floatVal = parseFloat(value) || 0;
    setAllocations(prev => ({
      ...prev,
      [invId]: floatVal
    }));
  };

  const autoApply = () => {
    const totalAvail = (parseFloat(amountReceived) || 0) + (useCredits ? parseFloat(availableCredits) : 0);
    let remaining = totalAvail;
    const newAllocs = {};
    
    unpaidList.forEach(inv => {
      if (remaining >= inv.balance_due) {
        newAllocs[inv.id] = inv.balance_due;
        remaining -= inv.balance_due;
      } else {
        newAllocs[inv.id] = parseFloat(remaining.toFixed(2));
        remaining = 0;
      }
    });

    // Populate remaining items with 0
    unpaidList.forEach(inv => {
      if (newAllocs[inv.id] === undefined) {
        newAllocs[inv.id] = 0;
      }
    });

    setAllocations(newAllocs);
  };

  // Calculations
  const totalDue = unpaidList.reduce((acc, curr) => acc + curr.balance_due, 0);
  const amountUsed = Object.values(allocations).reduce((acc, curr) => acc + curr, 0);
  const excess = (parseFloat(amountReceived) || 0) + (useCredits ? parseFloat(availableCredits) : 0) - amountUsed;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const allocationPayload = Object.keys(allocations).map(invId => ({
      invoice_id: parseInt(invId),
      amount: allocations[invId]
    })).filter(a => a.amount > 0);

    try {
      const res = await fetch(`${API_BASE}/payments`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          customer_id: parseInt(customerId),
          amount: parseFloat(amountReceived),
          date: payDate,
          method: payMode,
          notes,
          payment_number: payNumber,
          deposit_to: depositTo,
          bank_charges: parseFloat(bankCharges),
          reference,
          allocations: allocationPayload,
          use_credits: useCredits
        })
      });
      if (res.ok) {
        setShowForm(false);
        reload();
      } else {
        const data = await res.json();
        alert(data.error || 'Failed to save payment');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleVendorSubmit = async (e) => {
    e.preventDefault();
    const allocationPayload = Object.keys(billAllocations).map(bId => ({
      bill_id: parseInt(bId),
      amount: billAllocations[bId]
    })).filter(a => a.amount > 0);

    try {
      const res = await fetch(`${API_BASE}/payments`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          vendor_id: parseInt(vendorId),
          amount: parseFloat(amountPaid),
          date: payDate,
          method: payMode,
          notes,
          payment_number: payNumber,
          deposit_to: depositTo,
          reference,
          bank_charges: parseFloat(bankCharges),
          allocations: allocationPayload
        })
      });
      if (res.ok) {
        setShowForm(false);
        setVendorId('');
        setUnpaidBills([]);
        setBillAllocations({});
        setAmountPaid(0);
        reload();
      } else {
        const data = await res.json();
        alert(data.error || 'Failed to save vendor payment');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleExportPayments = () => {
    const headers = ['Payment Number', 'Customer Name', 'Vendor Name', 'Amount', 'Date', 'Method', 'Notes'];
    const mapping = ['payment_number', 'customer_name', 'vendor_name', 'amount', 'date', 'method', 'notes'];
    exportToCSV(payments, headers, mapping, 'payments_ledger');
  };

  return (
    <div>
      {!showForm && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
            <div>
              <h1 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>Payments Ledger</h1>
              <p style={{ color: 'var(--text-secondary)' }}>Track accounts receivable and accounts payable cash logs.</p>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={handleExportPayments} className="btn btn-secondary" style={{ border: '1px solid var(--border-color)' }}>
                <Download size={18} />
                <span>Export CSV</span>
              </button>
              <button onClick={() => { setPaymentDirection('inbound'); setShowForm(true); }} className="btn btn-primary">
                <ArrowUpRight size={18} />
                <span>Record Customer Payment</span>
              </button>
              <button onClick={() => { setPaymentDirection('outbound'); setShowForm(true); }} className="btn btn-secondary" style={{ border: '1px solid var(--border-color)' }}>
                <ArrowDownRight size={18} />
                <span>Record Vendor Payment</span>
              </button>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Payment #</th>
                  <th>Party Details</th>
                  <th>Direction</th>
                  <th>Invoice/Bill Reference</th>
                  <th>Amount</th>
                  <th>Date</th>
                  <th>Method</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {payments.map(p => (
                  <tr key={p.id}>
                    <td><strong>{p.payment_number || '-'}</strong></td>
                    <td>{p.customer_name ? p.customer_name : p.vendor_name ? p.vendor_name : '-'}</td>
                    <td>
                      <span style={{
                        padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem',
                        background: p.customer_name ? 'var(--success-bg)' : 'var(--danger-bg)',
                        color: p.customer_name ? 'var(--success)' : 'var(--danger)'
                      }}>
                        {p.customer_name ? 'Inbound' : 'Outbound'}
                      </span>
                    </td>
                    <td>{p.invoice_number ? `Invoice: ${p.invoice_number}` : p.bill_number ? `Bill: ${p.bill_number}` : '-'}</td>
                    <td>₹{p.amount.toFixed(2)}</td>
                    <td>{new Date(p.date).toLocaleDateString()}</td>
                    <td>{p.method}</td>
                    <td>{p.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {showForm && (
        <div className="card" style={{ maxWidth: '900px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
            <button type="button" onClick={() => setShowForm(false)} className="btn btn-secondary" style={{ padding: '8px' }}>
              <ChevronLeft size={16} />
            </button>
            <div>
              <h2 style={{ fontSize: '1.5rem', margin: 0 }}>
                {paymentDirection === 'inbound' ? 'Record Customer Payment (Inbound)' : 'Record Vendor Payment (Outbound)'}
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '2px' }}>
                {paymentDirection === 'inbound' ? 'Customer receivable against outstanding invoices' : 'Vendor payable against outstanding purchase bills'}
              </p>
            </div>
          </div>

          {/* Direction toggle inside form */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
            <button type="button" onClick={() => setPaymentDirection('inbound')} className={`bi-chart-tab${paymentDirection === 'inbound' ? ' active' : ''}`}>
              <ArrowUpRight size={14} /> Customer Payment
            </button>
            <button type="button" onClick={() => setPaymentDirection('outbound')} className={`bi-chart-tab${paymentDirection === 'outbound' ? ' active' : ''}`}>
              <ArrowDownRight size={14} /> Vendor Bill Payment
            </button>
          </div>

          {paymentDirection === 'outbound' ? (
            /* ── Outbound: Vendor Payment Form ── */
            <form onSubmit={handleVendorSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginBottom: '24px' }}>
                <div>
                  <div className="form-group">
                    <label className="form-label">Vendor*</label>
                    <select className="form-control" value={vendorId} onChange={e => setVendorId(e.target.value)} required>
                      <option value="">Select Vendor</option>
                      {vendors.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Amount Paid (₹)*</label>
                    <input className="form-control" type="number" step="any" min="0" value={amountPaid} onChange={e => setAmountPaid(parseFloat(e.target.value) || 0)} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Bank Charges</label>
                    <input className="form-control" type="number" step="any" min="0" value={bankCharges} onChange={e => setBankCharges(parseFloat(e.target.value) || 0)} />
                  </div>
                </div>
                <div>
                  <div className="form-group">
                    <label className="form-label">Payment Date*</label>
                    <input className="form-control" type="date" value={payDate} onChange={e => setPayDate(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Payment Mode</label>
                    <select className="form-control" value={payMode} onChange={e => setPayMode(e.target.value)}>
                      {['Bank Transfer', 'Cash', 'UPI', 'Cheque', 'NEFT', 'RTGS'].map(m => <option key={m}>{m}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Reference #</label>
                    <input className="form-control" type="text" value={reference} onChange={e => setReference(e.target.value)} placeholder="UTR / Cheque number" />
                  </div>
                </div>
              </div>

              {/* Unpaid Bills Allocation Table */}
              {unpaidBills.length > 0 && (
                <div style={{ marginBottom: '24px' }}>
                  <h4 style={{ marginBottom: '12px' }}>Allocate to Unpaid Bills</h4>
                  <div className="table-container" style={{ marginTop: 0 }}>
                    <table>
                      <thead>
                        <tr>
                          <th>Bill #</th>
                          <th>Date</th>
                          <th>Total</th>
                          <th>Balance Due</th>
                          <th>Allocate (₹)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {unpaidBills.map(b => (
                          <tr key={b.id}>
                            <td><strong>{b.bill_number}</strong></td>
                            <td>{new Date(b.date).toLocaleDateString()}</td>
                            <td>₹{b.grand_total?.toFixed(2)}</td>
                            <td style={{ color: 'var(--danger)', fontWeight: '600' }}>₹{b.balance_due?.toFixed(2)}</td>
                            <td>
                              <input type="number" step="any" min="0" max={b.balance_due} value={billAllocations[b.id] || 0} onChange={e => setBillAllocations(prev => ({ ...prev, [b.id]: parseFloat(e.target.value) || 0 }))} className="form-control" style={{ marginBottom: 0 }} />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <div className="form-group">
                <label className="form-label">Notes</label>
                <textarea className="form-control" rows="2" value={notes} onChange={e => setNotes(e.target.value)}></textarea>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
                <button type="button" onClick={() => setShowForm(false)} className="btn btn-secondary">Cancel</button>
                <button type="submit" className="btn btn-primary">Save Vendor Payment</button>
              </div>
            </form>
          ) : (
            /* ── Inbound: Customer Payment Form ── */
            <form onSubmit={handleSubmit}>
              {/* Header Layout: 2 Columns */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginBottom: '24px' }}>
                {/* Left Column */}
                <div>
                  <div className="form-group">
                    <label className="form-label">Customer Name*</label>
                    <select className="form-control" value={customerId} onChange={e => setCustomerId(e.target.value)} required>
                      <option value="">Select Customer</option>
                      {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{ color: 'var(--success)', fontWeight: 'bold', fontSize: '0.9rem' }}>Available Credits: ₹{availableCredits.toFixed(2)}</span>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
                    <input type="checkbox" checked={useCredits} onChange={e => setUseCredits(e.target.checked)} />
                    Use Available Credits
                  </label>
                </div>

                <div className="form-group">
                  <label className="form-label">Amount Received (₹)*</label>
                  <input className="form-control" type="number" step="any" min="0" value={amountReceived} onChange={e => setAmountReceived(parseFloat(e.target.value) || 0)} required />
                </div>

                <div className="form-group">
                  <label className="form-label">Bank Charges (if any)</label>
                  <input className="form-control" type="number" step="any" min="0" value={bankCharges} onChange={e => setBankCharges(parseFloat(e.target.value) || 0)} />
                </div>

                <div style={{ border: '1px solid var(--border-color)', borderRadius: '6px', padding: '12px', marginTop: '16px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px', fontSize: '0.9rem' }}>
                    <input type="checkbox" checked={taxDeducted} onChange={e => setTaxDeducted(e.target.checked)} />
                    Tax deducted?
                  </label>
                  {taxDeducted && (
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <input className="form-control" type="text" value={taxAccount} onChange={e => setTaxAccount(e.target.value)} placeholder="TDS Account" style={{ flex: 1 }} />
                      <input className="form-control" type="number" step="any" value={taxAmount} onChange={e => setTaxAmount(parseFloat(e.target.value) || 0)} placeholder="TDS Amount (₹)" style={{ width: '120px' }} />
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column */}
              <div>
                <div className="form-group">
                  <label className="form-label">Payment Date*</label>
                  <input className="form-control" type="date" value={payDate} onChange={e => setPayDate(e.target.value)} required />
                </div>

                <div className="form-group">
                  <label className="form-label">Payment #</label>
                  <input className="form-control" type="text" value={payNumber} onChange={e => setPayNumber(e.target.value)} />
                </div>

                <div className="form-group">
                  <label className="form-label">Payment Mode</label>
                  <select className="form-control" value={payMode} onChange={e => setPayMode(e.target.value)}>
                    <option value="Cash">Cash</option>
                    <option value="Bank Transfer">Bank Transfer</option>
                    <option value="UPI">UPI</option>
                    <option value="Cheque">Cheque</option>
                    <option value="Credit Card">Credit Card</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Deposit To</label>
                  <input className="form-control" type="text" value={depositTo} onChange={e => setDepositTo(e.target.value)} placeholder="e.g. Bank Account" />
                </div>

                <div className="form-group">
                  <label className="form-label">Reference#</label>
                  <input className="form-control" type="text" value={reference} onChange={e => setReference(e.target.value)} placeholder="e.g. TXN-12998" />
                </div>
              </div>
            </div>

            {/* Unpaid Invoices Section */}
            <div style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h4 style={{ margin: 0 }}>Unpaid Invoices</h4>
                <button type="button" className="btn btn-secondary" onClick={autoApply} style={{ padding: '6px 12px', fontSize: '0.85rem' }}>Auto Apply</button>
              </div>

              <div className="table-container" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Invoice #</th>
                      <th>Invoice Amount</th>
                      <th>Amount Due</th>
                      <th>Payment</th>
                    </tr>
                  </thead>
                  <tbody>
                    {unpaidList.map(inv => (
                      <tr key={inv.id}>
                        <td>{new Date(inv.date).toLocaleDateString()}</td>
                        <td>{inv.invoice_number}</td>
                        <td>₹{inv.grand_total.toFixed(2)}</td>
                        <td>₹{inv.balance_due.toFixed(2)}</td>
                        <td>
                          <input className="form-control" type="number" step="any" min="0" max={inv.balance_due} value={allocations[inv.id] || ''} onChange={e => handleAllocationChange(inv.id, e.target.value)} style={{ width: '130px', padding: '6px 10px' }} />
                        </td>
                      </tr>
                    ))}
                    {unpaidList.length === 0 && (
                      <tr>
                        <td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>Select a customer with unpaid invoices to allocate payment.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Footer Breakdown */}
            <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '30px', borderTop: '1px solid var(--border-color)', paddingTop: '20px', marginBottom: '30px' }}>
              {/* Notes and thank you check */}
              <div>
                <div className="form-group">
                  <label className="form-label">Notes (Internal use)</label>
                  <textarea className="form-control" rows="2" value={notes} onChange={e => setNotes(e.target.value)} placeholder="Internal notes..."></textarea>
                </div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
                  <input type="checkbox" checked={sendThankYou} onChange={e => setSendThankYou(e.target.checked)} />
                  Send a 'Thank you' note for this payment
                </label>
              </div>

              {/* Totals Breakdown */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end', fontSize: '0.95rem' }}>
                <div>Total Due: <strong style={{ marginLeft: '12px' }}>₹{totalDue.toFixed(2)}</strong></div>
                <div>Amount Used: <strong style={{ marginLeft: '12px' }}>₹{amountUsed.toFixed(2)}</strong></div>
                <div style={{ color: excess < 0 ? 'var(--danger)' : 'var(--success)' }}>
                  Amount Excess: <strong style={{ marginLeft: '12px' }}>₹{excess.toFixed(2)}</strong>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button type="button" onClick={() => setShowForm(false)} className="btn btn-secondary">Cancel</button>
              <button type="submit" className="btn btn-primary">Save Payment</button>
            </div>
          </form>
          )}
        </div>
      )}
    </div>
  );
}

// ==================== VIEW: STOCK FIFO ====================
function StockView({ getHeaders }) {
  const [stockValuation, setStockValuation] = useState([]);
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadStockData();
  }, []);

  const loadStockData = async () => {
    try {
      const resVal = await fetch(`${API_BASE}/stock/valuation`, { headers: getHeaders() });
      if (resVal.ok) setStockValuation(await resVal.json());

      const resBat = await fetch(`${API_BASE}/stock/batches`, { headers: getHeaders() });
      if (resBat.ok) setBatches(await resBat.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p style={{ color: 'var(--text-secondary)' }}>Calculating stock logs...</p>;

  // Search filter
  const filteredValuation = stockValuation.filter(sv => 
    sv.item_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredBatches = batches.filter(b => 
    b.item_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (b.vendor_name && b.vendor_name.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleExportValuation = () => {
    const headers = ['Item Name', 'Qty Purchased', 'Qty Sold', 'Qty Remaining', 'Avg Purchase Cost', 'Total Asset Value', 'Base Selling Price'];
    const mapping = ['item_name', 'total_purchased', 'total_sold', 'total_quantity', 'avg_cost', 'total_value', 'selling_price'];
    exportToCSV(filteredValuation, headers, mapping, 'stock_valuation_summary');
  };

  const handleExportBatches = () => {
    const headers = ['Batch ID', 'Item Name', 'Purchase Date', 'Remaining Qty', 'Purchase Cost', 'Supplier'];
    const mapping = ['id', 'item_name', 'purchase_date', 'quantity_remaining', 'purchase_rate', 'vendor_name'];
    exportToCSV(filteredBatches, headers, mapping, 'stock_batches_log');
  };

  return (
    <div className="print-area">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>FIFO Inventory Valuation</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Breakdown of item batches based on First-In-First-Out (FIFO) methodology.</p>
        </div>
        <div className="no-print" style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => window.print()} className="btn btn-primary">
            <Download size={18} />
            <span>Print Stock Report</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }} className="no-print">
        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'rgba(99,102,241,0.15)' }}>
            <Layers size={22} style={{ color: '#6366f1' }} />
          </div>
          <div>
            <p className="kpi-label">Remaining stock</p>
            <p className="kpi-value">{filteredValuation.reduce((acc, v) => acc + v.total_quantity, 0).toLocaleString()} units</p>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'rgba(16,185,129,0.15)' }}>
            <TrendingUp size={22} style={{ color: '#10b981' }} />
          </div>
          <div>
            <p className="kpi-label">Total Sold (Qty)</p>
            <p className="kpi-value">{filteredValuation.reduce((acc, v) => acc + v.total_sold, 0).toLocaleString()} units</p>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'rgba(245,158,11,0.15)' }}>
            <Receipt size={22} style={{ color: '#f59e0b' }} />
          </div>
          <div>
            <p className="kpi-label">Asset Valuation</p>
            <p className="kpi-value">₹{filteredValuation.reduce((acc, v) => acc + v.total_value, 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
          </div>
        </div>
      </div>

      {/* Search Input */}
      <div className="no-print" style={{ marginBottom: '24px' }}>
        <input 
          type="text" 
          className="form-control" 
          placeholder="Search inventory items by name..." 
          value={searchQuery} 
          onChange={e => setSearchQuery(e.target.value)} 
          style={{ maxWidth: '400px', marginBottom: 0 }}
        />
      </div>

      <div className="card" style={{ marginBottom: '40px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ margin: 0 }}>Stock Valuation Summary</h3>
          <button onClick={handleExportValuation} className="btn btn-secondary no-print" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>Export CSV</button>
        </div>
        <div className="table-container" style={{ marginTop: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Item Name</th>
                <th>Qty Purchased</th>
                <th>Qty Sold</th>
                <th>Qty Remaining</th>
                <th>Avg Purchase Cost</th>
                <th>Total Asset Value</th>
                <th>Base Selling Price</th>
                <th>Potential Margin</th>
              </tr>
            </thead>
            <tbody>
              {filteredValuation.map(sv => {
                const margin = sv.selling_price > 0 
                  ? (((sv.selling_price - sv.avg_cost) / sv.selling_price) * 100).toFixed(1)
                  : '0.0';
                return (
                  <tr key={sv.item_id}>
                    <td><strong>{sv.item_name}</strong></td>
                    <td>{sv.total_purchased} pcs</td>
                    <td style={{ color: 'var(--success)', fontWeight: '600' }}>{sv.total_sold} pcs</td>
                    <td style={{ fontWeight: 'bold' }}>{sv.total_quantity} pcs</td>
                    <td>₹{sv.avg_cost.toFixed(2)}</td>
                    <td>₹{sv.total_value.toFixed(2)}</td>
                    <td>₹{sv.selling_price.toFixed(2)}</td>
                    <td style={{ color: parseFloat(margin) > 0 ? 'var(--success)' : 'inherit' }}>
                      {margin}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ margin: 0 }}>Stock Batches Log</h3>
          <button onClick={handleExportBatches} className="btn btn-secondary no-print" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>Export CSV</button>
        </div>
        <div className="table-container" style={{ marginTop: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Batch ID</th>
                <th>Item Name</th>
                <th>Purchase Date</th>
                <th>Remaining Qty</th>
                <th>Purchase Cost</th>
                <th>Associated Supplier</th>
              </tr>
            </thead>
            <tbody>
              {filteredBatches.map(b => (
                <tr key={b.id} style={{ opacity: b.quantity_remaining === 0 ? 0.5 : 1 }}>
                  <td>#{b.id}</td>
                  <td><strong>{b.item_name}</strong></td>
                  <td>{new Date(b.purchase_date).toLocaleDateString()}</td>
                  <td>{b.quantity_remaining} pcs</td>
                  <td>₹{b.purchase_rate.toFixed(2)}</td>
                  <td>{b.vendor_name || 'Opening Stock'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ==================== VIEW: REPORTS ====================
function ReportsView({ getHeaders }) {
  const [reportType, setReportType] = useState('gst');
  const [gstSummary, setGstSummary] = useState(null);
  const [agingSummary, setAgingSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Custom date ranges
  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - 30);
    return d.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split('T')[0]);

  useEffect(() => {
    fetchReport();
  }, [reportType, startDate, endDate]);

  const fetchReport = async () => {
    setLoading(true);
    try {
      if (reportType === 'gst') {
        const res = await fetch(`${API_BASE}/reports/gst-summary?startDate=${startDate}&endDate=${endDate}`, { headers: getHeaders() });
        if (res.ok) setGstSummary(await res.json());
      } else if (reportType === 'aging') {
        const res = await fetch(`${API_BASE}/reports/aging/receivables`, { headers: getHeaders() });
        if (res.ok) setAgingSummary(await res.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="print-area">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>Business Intelligence Reports</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Review tax breakdown and accounts receivable aging summaries.</p>
        </div>
        <button onClick={() => window.print()} className="btn btn-primary no-print">
          <Download size={18} />
          <span>Print / Save PDF</span>
        </button>
      </div>

      {/* Date Pickers (only shown for GST report) */}
      {reportType === 'gst' && (
        <div className="no-print" style={{ display: 'flex', gap: '16px', marginBottom: '24px', background: 'var(--bg-secondary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', alignItems: 'center' }}>
          <span style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>Filter Date Range:</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>From:</label>
            <input type="date" className="form-control" value={startDate} onChange={e => setStartDate(e.target.value)} style={{ width: '160px', marginBottom: 0 }} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>To:</label>
            <input type="date" className="form-control" value={endDate} onChange={e => setEndDate(e.target.value)} style={{ width: '160px', marginBottom: 0 }} />
          </div>
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', marginBottom: '24px', gap: '16px' }}>
        <button onClick={() => setReportType('gst')} style={{ background: 'none', border: 'none', borderBottom: reportType === 'gst' ? '2px solid var(--accent-primary)' : 'none', color: reportType === 'gst' ? 'var(--text-primary)' : 'var(--text-secondary)', padding: '12px 16px', cursor: 'pointer', fontWeight: reportType === 'gst' ? '600' : '400' }}>
          GST Input / Output Summary
        </button>
        <button onClick={() => setReportType('aging')} style={{ background: 'none', border: 'none', borderBottom: reportType === 'aging' ? '2px solid var(--accent-primary)' : 'none', color: reportType === 'aging' ? 'var(--text-primary)' : 'var(--text-secondary)', padding: '12px 16px', cursor: 'pointer', fontWeight: reportType === 'aging' ? '600' : '400' }}>
          Receivables Overdue Aging
        </button>
      </div>

      {loading && <p style={{ color: 'var(--text-secondary)' }}>Extracting dataset report...</p>}

      {!loading && reportType === 'gst' && gstSummary && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
          <div className="card">
            <h3 style={{ marginBottom: '16px', color: 'var(--success)' }}>Output GST (Collected on Sales)</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>GST Slabs</th>
                    <th>Total Tax Collected</th>
                  </tr>
                </thead>
                <tbody>
                  {gstSummary.salesTax?.map((row, idx) => (
                    <tr key={idx}>
                      <td>GST @ {row.gst_percent}%</td>
                      <td>₹{row.tax_collected ? parseFloat(row.tax_collected).toFixed(2) : '0.00'}</td>
                    </tr>
                  ))}
                  {(!gstSummary.salesTax || gstSummary.salesTax.length === 0) && (
                    <tr><td colSpan="2" style={{ color: 'var(--text-muted)' }}>No sales record found.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginBottom: '16px', color: 'var(--info)' }}>Input GST (Paid on Purchases)</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>GST Slabs</th>
                    <th>Total Tax Paid</th>
                  </tr>
                </thead>
                <tbody>
                  {gstSummary.purchaseTax?.map((row, idx) => (
                    <tr key={idx}>
                      <td>GST @ {row.gst_percent}%</td>
                      <td>₹{row.tax_paid ? parseFloat(row.tax_paid).toFixed(2) : '0.00'}</td>
                    </tr>
                  ))}
                  {(!gstSummary.purchaseTax || gstSummary.purchaseTax.length === 0) && (
                    <tr><td colSpan="2" style={{ color: 'var(--text-muted)' }}>No purchase bills found.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {!loading && reportType === 'aging' && agingSummary && (
        <div>
          {/* Aging metrics bar */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px', marginBottom: '30px' }}>
            {[
              { label: 'Current', val: agingSummary.current, color: 'var(--success)' },
              { label: '1 - 30 Days', val: agingSummary.thirty, color: 'var(--info)' },
              { label: '31 - 60 Days', val: agingSummary.sixty, color: 'var(--warning)' },
              { label: '61 - 90 Days', val: agingSummary.ninety, color: 'var(--danger)' },
              { label: '90+ Days Due', val: agingSummary.ninetyPlus, color: '#991b1b' },
            ].map((col, idx) => (
              <div key={idx} className="card" style={{ padding: '16px', textAlign: 'center', borderTop: `4px solid ${col.color}` }}>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{col.label}</p>
                <h4 style={{ fontSize: '1.2rem', marginTop: '8px' }}>₹{col.val.toLocaleString('en-IN')}</h4>
              </div>
            ))}
          </div>

          <div className="card">
            <h3 style={{ marginBottom: '16px' }}>Invoice Aging Log</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Invoice No</th>
                    <th>Customer Name</th>
                    <th>Invoice Date</th>
                    <th>Due Date</th>
                    <th>Days Overdue</th>
                    <th>Balance Due</th>
                  </tr>
                </thead>
                <tbody>
                  {agingSummary.details?.map((detail, idx) => (
                    <tr key={idx}>
                      <td><strong>{detail.invoice_number}</strong></td>
                      <td>{detail.customer_name}</td>
                      <td>{new Date(detail.date).toLocaleDateString()}</td>
                      <td>{new Date(detail.due_date).toLocaleDateString()}</td>
                      <td style={{ color: detail.days_overdue > 30 ? 'var(--danger)' : 'inherit' }}>
                        {detail.days_overdue} days
                      </td>
                      <td style={{ fontWeight: 'bold' }}>₹{detail.balance.toFixed(2)}</td>
                    </tr>
                  ))}
                  {(!agingSummary.details || agingSummary.details.length === 0) && (
                    <tr><td colSpan="6" style={{ color: 'var(--text-muted)' }}>All receivables are fully cleared!</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ==================== VIEW: SETTINGS ====================
function SettingsView({ settings, getHeaders, reload, token, outlets, theme, setTheme, user }) {
  const isAdmin = user?.role === 'Admin';
  const [activeSubTab, setActiveSubTab] = useState(isAdmin ? 'profile' : 'appearance');
  const [companyName, setCompanyName] = useState('');
  const [companyAddress, setCompanyAddress] = useState('');
  const [companyGstin, setCompanyGstin] = useState('');
  const [companyState, setCompanyState] = useState('');
  const [invoicePrefix, setInvoicePrefix] = useState('');
  const [companyLogo, setCompanyLogo] = useState('');
  const [companyUpiId, setCompanyUpiId] = useState('');
  const [sp1Label, setSp1Label] = useState('Type 1 pricing');
  const [sp2Label, setSp2Label] = useState('Type 2 pricing');
  const [sp3Label, setSp3Label] = useState('Type 3 pricing');
  const [msg, setMsg] = useState('');

  // Database Connection States
  const [dbHost, setDbHost] = useState('');
  const [dbPort, setDbPort] = useState(3306);
  const [dbUser, setDbUser] = useState('');
  const [dbPassword, setDbPassword] = useState('');
  const [dbName, setDbName] = useState('');
  const [dbMsg, setDbMsg] = useState('');

  // Staff States
  const [users, setUsers] = useState([]);
  const [newUserName, setNewUserName] = useState('');
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserPassword, setNewUserPassword] = useState('');
  const [newUserRole, setNewUserRole] = useState('Store Staff');
  const [newUserOutlet, setNewUserOutlet] = useState(1);
  const [staffMsg, setStaffMsg] = useState('');

  // Outlet States
  const [selectedOutletEdit, setSelectedOutletEdit] = useState(null);
  const [outletName, setOutletName] = useState('');
  const [outletLocation, setOutletLocation] = useState('');
  const [outletPricingType, setOutletPricingType] = useState('Base');
  const [outletLogoUrl, setOutletLogoUrl] = useState('');
  const [outletAddress, setOutletAddress] = useState('');
  const [outletGstin, setOutletGstin] = useState('');
  const [outletState, setOutletState] = useState('');
  const [outletPhone, setOutletPhone] = useState('');
  const [outletEmail, setOutletEmail] = useState('');
  const [outletUpiId, setOutletUpiId] = useState('');
  const [outletMsg, setOutletMsg] = useState('');

  useEffect(() => {
    if (settings) {
      setCompanyName(settings.company_name || '');
      setCompanyAddress(settings.company_address || '');
      setCompanyGstin(settings.company_gstin || '');
      setCompanyState(settings.company_state || '');
      setInvoicePrefix(settings.invoice_prefix || '');
      setCompanyLogo(settings.company_logo || '');
      setCompanyUpiId(settings.company_upi_id || '');
      setSp1Label(settings.sp1_label || 'Type 1 pricing');
      setSp2Label(settings.sp2_label || 'Type 2 pricing');
      setSp3Label(settings.sp3_label || 'Type 3 pricing');
    }
  }, [settings]);

  useEffect(() => {
    if (activeSubTab === 'staff') {
      loadUsers();
    } else if (activeSubTab === 'backup') {
      loadDatabaseConfig();
    }
  }, [activeSubTab]);

  const loadUsers = async () => {
    try {
      const res = await fetch(`${API_BASE}/admin/users`, { headers: getHeaders() });
      if (res.ok) setUsers(await res.json());
    } catch (err) {
      console.error(err);
    }
  };

  const loadDatabaseConfig = async () => {
    try {
      const res = await fetch(`${API_BASE}/settings/database`, { headers: getHeaders() });
      if (res.ok) {
        const data = await res.json();
        setDbHost(data.host || 'localhost');
        setDbPort(data.port || 3306);
        setDbUser(data.user || 'root');
        setDbPassword(data.password || '');
        setDbName(data.database || 'ledgerpro');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDatabaseSubmit = async (e) => {
    e.preventDefault();
    setDbMsg('');
    try {
      const res = await fetch(`${API_BASE}/settings/database`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          host: dbHost,
          port: dbPort,
          user: dbUser,
          password: dbPassword,
          database: dbName
        })
      });
      const d = await res.json();
      if (res.ok) {
        setDbMsg(d.message);
      } else {
        setDbMsg('Error: ' + d.error);
      }
    } catch (err) {
      setDbMsg('Error: ' + err.message);
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/settings`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          company_name: companyName,
          company_address: companyAddress,
          company_gstin: companyGstin,
          company_state: companyState,
          invoice_prefix: invoicePrefix,
          company_logo: companyLogo,
          company_upi_id: companyUpiId,
          sp1_label: sp1Label,
          sp2_label: sp2Label,
          sp3_label: sp3Label
        })
      });
      if (res.ok) {
        setMsg('Profile configurations saved.');
        reload();
        setTimeout(() => setMsg(''), 3000);
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleCreateStaff = async (e) => {
    e.preventDefault();
    setStaffMsg('');
    try {
      const res = await fetch(`${API_BASE}/admin/users`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          name: newUserName,
          email: newUserEmail,
          password: newUserPassword,
          role: newUserRole,
          outlet_id: parseInt(newUserOutlet)
        })
      });
      const data = await res.json();
      if (res.ok) {
        setStaffMsg('Staff user account created successfully!');
        setNewUserName('');
        setNewUserEmail('');
        setNewUserPassword('');
        loadUsers();
      } else {
        setStaffMsg('Error: ' + data.error);
      }
    } catch (err) {
      setStaffMsg('Error: ' + err.message);
    }
  };

  const handleDeleteStaff = async (userId) => {
    if (!confirm('Are you sure you want to remove this staff user?')) return;
    try {
      const res = await fetch(`${API_BASE}/admin/users/${userId}`, {
        method: 'DELETE',
        headers: getHeaders()
      });
      if (res.ok) {
        loadUsers();
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleCreateOutlet = async (e) => {
    e.preventDefault();
    setOutletMsg('');
    try {
      const endpoint = selectedOutletEdit
        ? `${API_BASE}/outlets/${selectedOutletEdit.id}`
        : `${API_BASE}/outlets`;
      const method = selectedOutletEdit ? 'PUT' : 'POST';
      const res = await fetch(endpoint, {
        method,
        headers: getHeaders(),
        body: JSON.stringify({
          name: outletName,
          location: outletLocation,
          pricing_type: outletPricingType,
          logo_url: outletLogoUrl,
          address: outletAddress,
          gstin: outletGstin,
          state: outletState,
          phone: outletPhone,
          email: outletEmail,
          upi_id: outletUpiId
        })
      });
      if (res.ok) {
        setOutletMsg(selectedOutletEdit ? 'Outlet updated successfully!' : 'Outlet created successfully!');
        setOutletName('');
        setOutletLocation('');
        setOutletPricingType('Base');
        setOutletLogoUrl('');
        setOutletAddress('');
        setOutletGstin('');
        setOutletState('');
        setOutletPhone('');
        setOutletEmail('');
        setOutletUpiId('');
        setSelectedOutletEdit(null);
        reload();
      } else {
        const d = await res.json();
        setOutletMsg('Error: ' + d.error);
      }
    } catch (err) {
      setOutletMsg('Error: ' + err.message);
    }
  };

  const handleEditOutlet = (outlet) => {
    setSelectedOutletEdit(outlet);
    setOutletName(outlet.name);
    setOutletLocation(outlet.location || '');
    setOutletPricingType(outlet.pricing_type || 'Base');
    setOutletLogoUrl(outlet.logo_url || '');
    setOutletAddress(outlet.address || '');
    setOutletGstin(outlet.gstin || '');
    setOutletState(outlet.state || '');
    setOutletPhone(outlet.phone || '');
    setOutletEmail(outlet.email || '');
    setOutletUpiId(outlet.upi_id || '');
  };

  const handleDeleteOutlet = async (id) => {
    if (!confirm('Are you sure you want to delete this outlet?')) return;
    try {
      const res = await fetch(`${API_BASE}/outlets/${id}`, {
        method: 'DELETE',
        headers: getHeaders()
      });
      if (res.ok) {
        reload();
      }
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>Business Settings</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Manage business details, logos, and staff account roles.</p>
      </div>

      {/* Sub Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', marginBottom: '24px', gap: '4px', flexWrap: 'wrap' }}>
        {[
          { id: 'profile', label: 'Business Profile', icon: <Building2 size={15} />, adminOnly: true },
          { id: 'appearance', label: 'Appearance', icon: <Palette size={15} /> },
          { id: 'staff', label: 'Staff Management', icon: <Users size={15} />, adminOnly: true },
          { id: 'outlets', label: 'Outlet Management', icon: <Store size={15} />, adminOnly: true },
          { id: 'backup', label: 'Data & Backup', icon: <Database size={15} />, adminOnly: true },
        ].filter(tab => !tab.adminOnly || user?.role === 'Admin').map(tab => (
          <button key={tab.id} onClick={() => setActiveSubTab(tab.id)} style={{ background: 'none', border: 'none', borderBottom: activeSubTab === tab.id ? '2px solid var(--accent-primary)' : '2px solid transparent', color: activeSubTab === tab.id ? 'var(--text-primary)' : 'var(--text-secondary)', padding: '12px 16px', cursor: 'pointer', fontWeight: activeSubTab === tab.id ? '600' : '400', display: 'inline-flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem', transition: 'all 0.15s' }}>
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {activeSubTab === 'profile' && isAdmin && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '30px' }}>
          <div className="card">
            {msg && <div style={{ background: 'var(--success-bg)', color: 'var(--success)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '10px', borderRadius: 'var(--border-radius-sm)', marginBottom: '16px', fontSize: '0.9rem' }}>{msg}</div>}
            <form onSubmit={handleProfileSubmit}>
              <div className="form-group">
                <label className="form-label">Registered Business Name</label>
                <input className="form-control" type="text" value={companyName} onChange={e => setCompanyName(e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">Company Logo URL</label>
                <input className="form-control" type="text" value={companyLogo} onChange={e => setCompanyLogo(e.target.value)} placeholder="https://example.com/logo.png" />
              </div>
              <div className="form-group">
                <label className="form-label">Business Address</label>
                <textarea className="form-control" rows="3" value={companyAddress} onChange={e => setCompanyAddress(e.target.value)} required></textarea>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                <div className="form-group">
                  <label className="form-label">State Jurisdiction</label>
                  <input className="form-control" type="text" value={companyState} onChange={e => setCompanyState(e.target.value)} required placeholder="e.g. Haryana" />
                </div>
                <div className="form-group">
                  <label className="form-label">Company GSTIN</label>
                  <input className="form-control" type="text" value={companyGstin} onChange={e => setCompanyGstin(e.target.value)} placeholder="15-character GSTIN number" />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                <div className="form-group">
                  <label className="form-label">Invoice Number Prefix</label>
                  <input className="form-control" type="text" value={invoicePrefix} onChange={e => setInvoicePrefix(e.target.value)} required placeholder="e.g. INV-" />
                </div>
                <div className="form-group">
                  <label className="form-label">Default UPI ID (for Invoices QR Code)</label>
                  <input className="form-control" type="text" value={companyUpiId} onChange={e => setCompanyUpiId(e.target.value)} placeholder="e.g. business@okaxis" />
                </div>
              </div>
              <h4 style={{ margin: '20px 0 12px' }}>Custom Pricing Labels (Selling Price Tiers)</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '30px' }}>
                <div className="form-group">
                  <label className="form-label">SP1 Custom Label</label>
                  <input className="form-control" type="text" value={sp1Label} onChange={e => setSp1Label(e.target.value)} required />
                </div>
                <div className="form-group">
                  <label className="form-label">SP2 Custom Label</label>
                  <input className="form-control" type="text" value={sp2Label} onChange={e => setSp2Label(e.target.value)} required />
                </div>
                <div className="form-group">
                  <label className="form-label">SP3 Custom Label</label>
                  <input className="form-control" type="text" value={sp3Label} onChange={e => setSp3Label(e.target.value)} required />
                </div>
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
                Save Configurations
              </button>
            </form>
          </div>

          <div>
            <div className="card" style={{ marginBottom: '20px' }}>
              <h3 style={{ marginBottom: '12px' }}>Logo Preview</h3>
              <div style={{ height: '120px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px dashed var(--border-color)', borderRadius: '8px', padding: '10px' }}>
                {companyLogo ? (
                  <img src={companyLogo} alt="Company Logo" style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }} onError={e => e.target.style.display = 'none'} />
                ) : (
                  <span style={{ color: 'var(--text-muted)' }}>No logo configured</span>
                )}
              </div>
            </div>

            <div className="card">
              <h3 style={{ marginBottom: '12px' }}>Database Administration</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '20px' }}>Generate a complete SQL export/dump of all schema and records in the LedgerPro database.</p>
              <a href={`${API_BASE}/settings/backup?token=${token}`} download className="btn btn-secondary" style={{ width: '100%', textDecoration: 'none', display: 'inline-flex', justifyContent: 'center', backgroundColor: '#1e3a8a', color: 'white', border: 'none', padding: '12px', alignItems: 'center', gap: '8px' }}>
                <Database size={16} />
                <span>Backup Database (SQL Dump)</span>
              </a>
            </div>
          </div>
        </div>
      )}

      {/* ── Appearance Tab ── */}
      {activeSubTab === 'appearance' && (
        <div style={{ maxWidth: '700px' }}>
          <div className="card" style={{ marginBottom: '24px' }}>
            <h3 style={{ marginBottom: '6px' }}>UI Theme</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '24px' }}>Choose a colour scheme for the application. Your preference is saved in the browser.</p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
              {[
                { id: 'dark',    label: 'Midnight Dark',  bg: '#0b0f19', accent: '#6366f1' },
                { id: 'light',   label: 'Crisp Light',    bg: '#f1f5f9', accent: '#6366f1' },
                { id: 'ocean',   label: 'Ocean Blue',     bg: '#040d1a', accent: '#0ea5e9' },
                { id: 'emerald', label: 'Emerald Forest', bg: '#021a0e', accent: '#10b981' },
                { id: 'rose',    label: 'Rose Gold',      bg: '#1a0608', accent: '#e11d48' },
                { id: 'slate',   label: 'Slate Pro',      bg: '#1e2433', accent: '#667eea' },
              ].map(t => (
                <button
                  key={t.id}
                  onClick={() => setTheme(t.id)}
                  style={{
                    background: t.bg,
                    border: `3px solid ${theme === t.id ? t.accent : 'transparent'}`,
                    borderRadius: '12px', padding: '20px 16px', cursor: 'pointer',
                    transition: 'all 0.2s', transform: theme === t.id ? 'scale(1.03)' : 'scale(1)',
                    boxShadow: theme === t.id ? `0 0 20px ${t.accent}40` : '0 2px 8px rgba(0,0,0,0.3)',
                    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px'
                  }}
                >
                  {/* Mini preview */}
                  <div style={{ width: '100%', height: '60px', borderRadius: '8px', overflow: 'hidden', position: 'relative', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <div style={{ position: 'absolute', top: 0, left: 0, width: '30%', height: '100%', background: `${t.accent}22` }}></div>
                    <div style={{ position: 'absolute', top: '10px', right: '8px', width: '50%', height: '10px', borderRadius: '4px', background: t.accent, opacity: 0.9 }}></div>
                    <div style={{ position: 'absolute', top: '26px', right: '8px', width: '35%', height: '6px', borderRadius: '4px', background: 'rgba(255,255,255,0.2)' }}></div>
                    <div style={{ position: 'absolute', top: '38px', right: '8px', width: '44%', height: '6px', borderRadius: '4px', background: 'rgba(255,255,255,0.1)' }}></div>
                    {theme === t.id && (
                      <div style={{ position: 'absolute', top: '4px', left: '4px', width: '20px', height: '20px', borderRadius: '50%', background: t.accent, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Check size={12} style={{ color: 'white' }} />
                      </div>
                    )}
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <p style={{ color: theme === t.id ? t.accent : 'rgba(255,255,255,0.7)', fontWeight: theme === t.id ? '700' : '500', fontSize: '0.85rem' }}>{t.label}</p>
                    {theme === t.id && <p style={{ fontSize: '0.72rem', color: t.accent, marginTop: '2px' }}>Active</p>}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginBottom: '12px' }}>Display Preferences</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div style={{ padding: '16px', border: '1px solid var(--border-color)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <p style={{ fontWeight: '600', fontSize: '0.9rem' }}>Compact Sidebar</p>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>Collapse sidebar by default</p>
                </div>
                <span style={{ padding: '4px 10px', borderRadius: '20px', fontSize: '0.75rem', background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>User Preference</span>
              </div>
              <div style={{ padding: '16px', border: '1px solid var(--border-color)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <p style={{ fontWeight: '600', fontSize: '0.9rem' }}>Currency Symbol</p>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>Indian Rupee (₹)</p>
                </div>
                <span style={{ padding: '4px 10px', borderRadius: '20px', fontSize: '0.75rem', background: 'var(--success-bg)', color: 'var(--success)' }}>INR</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Data & Backup Tab ── */}
      {activeSubTab === 'backup' && isAdmin && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
          <div>
            <div className="card" style={{ marginBottom: '20px' }}>
              <h3 style={{ marginBottom: '12px' }}>Database Administration</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '20px' }}>Generate a complete SQL export/dump of all schema and records in the LedgerPro database.</p>
              <a href={`${API_BASE}/settings/backup?token=${token}`} download className="btn btn-primary" style={{ width: '100%', textDecoration: 'none', display: 'inline-flex', justifyContent: 'center', padding: '14px', alignItems: 'center', gap: '8px' }}>
                <Download size={16} />
                <span>Download Full SQL Backup</span>
              </a>
            </div>
            
            <div className="card" style={{ border: '1px solid rgba(239,68,68,0.3)' }}>
              <h3 style={{ marginBottom: '8px', color: 'var(--danger)' }}>Danger Zone</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '16px' }}>Destructive operations — these actions cannot be undone. Ensure you have a backup first.</p>
              <button className="btn" style={{ background: 'var(--danger-bg)', color: 'var(--danger)', border: '1px solid rgba(239,68,68,0.3)', width: '100%', justifyContent: 'center', padding: '12px' }} disabled>
                <AlertTriangle size={16} />
                <span>Wipe & Reset (Coming Soon)</span>
              </button>
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginBottom: '16px' }}>Database Connection Settings</h3>
            {dbMsg && (
              <div style={{ background: dbMsg.includes('Error') ? 'var(--danger-bg)' : 'var(--success-bg)', color: dbMsg.includes('Error') ? 'var(--danger)' : 'var(--success)', border: '1px solid rgba(0,0,0,0.1)', padding: '10px', borderRadius: '8px', marginBottom: '16px', fontSize: '0.85rem' }}>
                {dbMsg}
              </div>
            )}
            <form onSubmit={handleDatabaseSubmit}>
              <div className="form-group">
                <label className="form-label">Database Host</label>
                <input className="form-control" type="text" value={dbHost} onChange={e => setDbHost(e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">Database Port</label>
                <input className="form-control" type="number" value={dbPort} onChange={e => setDbPort(parseInt(e.target.value) || 3306)} required />
              </div>
              <div className="form-group">
                <label className="form-label">Username</label>
                <input className="form-control" type="text" value={dbUser} onChange={e => setDbUser(e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input className="form-control" type="password" value={dbPassword} onChange={e => setDbPassword(e.target.value)} placeholder="Leave blank if none" />
              </div>
              <div className="form-group">
                <label className="form-label">Database Name</label>
                <input className="form-control" type="text" value={dbName} onChange={e => setDbName(e.target.value)} required />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '16px' }}>
                Save Database Config
              </button>
            </form>
          </div>
        </div>
      )}

      {activeSubTab === 'staff' && isAdmin && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '30px' }}>
          {/* User List */}
          <div className="card">
            <h3 style={{ marginBottom: '16px' }}>Configured Staff Accounts</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Assigned Branch</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id}>
                      <td><strong>{u.name}</strong></td>
                      <td>{u.email}</td>
                      <td>
                        <span style={{ padding: '3px 8px', borderRadius: '4px', fontSize: '0.8rem', backgroundColor: u.role === 'Admin' ? 'var(--accent-primary)' : 'var(--bg-tertiary)' }}>
                          {u.role}
                        </span>
                      </td>
                      <td>{u.outlet_name || 'Main Outlet'}</td>
                      <td>
                        <button onClick={() => handleDeleteStaff(u.id)} className="btn btn-danger" style={{ padding: '4px 8px', fontSize: '0.75rem' }}>Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Add Staff form */}
          <div className="card">
            <h3 style={{ marginBottom: '16px' }}>Add Staff User</h3>
            {staffMsg && (
              <div style={{ background: staffMsg.includes('Error') ? 'var(--danger-bg)' : 'var(--success-bg)', color: staffMsg.includes('Error') ? 'var(--danger)' : 'var(--success)', padding: '10px', borderRadius: '4px', marginBottom: '16px', fontSize: '0.85rem' }}>
                {staffMsg}
              </div>
            )}
            <form onSubmit={handleCreateStaff}>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input className="form-control" type="text" value={newUserName} onChange={e => setNewUserName(e.target.value)} required placeholder="Staff Full Name" />
              </div>
              <div className="form-group">
                <label className="form-label">Email address</label>
                <input className="form-control" type="email" value={newUserEmail} onChange={e => setNewUserEmail(e.target.value)} required placeholder="staff@outlet.com" />
              </div>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input className="form-control" type="password" value={newUserPassword} onChange={e => setNewUserPassword(e.target.value)} required placeholder="••••••••" />
              </div>
              <div className="form-group">
                <label className="form-label">System Role</label>
                <select className="form-control" value={newUserRole} onChange={e => setNewUserRole(e.target.value)}>
                  <option value="Store Staff">Store Staff</option>
                  <option value="Admin">Admin</option>
                </select>
              </div>
              <div className="form-group" style={{ marginBottom: '24px' }}>
                <label className="form-label">Assigned Outlet</label>
                <select className="form-control" value={newUserOutlet} onChange={e => setNewUserOutlet(e.target.value)}>
                  {outlets.map(o => <option key={o.id} value={o.id}>{o.name} ({o.location})</option>)}
                </select>
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Create User Account</button>
            </form>
          </div>
        </div>
      )}

      {activeSubTab === 'outlets' && isAdmin && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '30px' }}>
          {/* Outlets List */}
          <div className="card">
            <h3 style={{ marginBottom: '16px' }}>Configured Enterprise Branches</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Branch Name</th>
                    <th>Location / Address</th>
                    <th>Default Pricing Tier</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {outlets.map(o => (
                    <tr key={o.id}>
                      <td><strong>{o.name}</strong></td>
                      <td>{o.location || '-'}</td>
                      <td>
                        <span style={{ padding: '3px 8px', borderRadius: '4px', fontSize: '0.8rem', backgroundColor: 'var(--bg-tertiary)' }}>
                          {o.pricing_type === 'Base' ? 'Base Price' : o.pricing_type === 'SP1' ? sp1Label : o.pricing_type === 'SP2' ? sp2Label : sp3Label}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button onClick={() => handleEditOutlet(o)} className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '0.75rem' }}>Edit</button>
                          <button onClick={() => handleDeleteOutlet(o.id)} className="btn btn-danger" style={{ padding: '4px 8px', fontSize: '0.75rem' }}>Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Add / Edit Outlet Form */}
          <div className="card">
            <h3 style={{ marginBottom: '16px' }}>{selectedOutletEdit ? 'Edit Branch' : 'Add New Branch'}</h3>
            {outletMsg && (
              <div style={{ background: outletMsg.includes('Error') ? 'var(--danger-bg)' : 'var(--success-bg)', color: outletMsg.includes('Error') ? 'var(--danger)' : 'var(--success)', padding: '10px', borderRadius: '4px', marginBottom: '16px', fontSize: '0.85rem' }}>
                {outletMsg}
              </div>
            )}
            <form onSubmit={handleCreateOutlet}>
              <div className="form-group">
                <label className="form-label">Branch Name</label>
                <input className="form-control" type="text" value={outletName} onChange={e => setOutletName(e.target.value)} required placeholder="e.g. North Branch" />
              </div>
              <div className="form-group">
                <label className="form-label">Branch Logo URL</label>
                <input className="form-control" type="text" value={outletLogoUrl} onChange={e => setOutletLogoUrl(e.target.value)} placeholder="https://example.com/branch-logo.png" />
              </div>
              <div className="form-group">
                <label className="form-label">Branch Address</label>
                <textarea className="form-control" rows="2" value={outletAddress} onChange={e => setOutletAddress(e.target.value)} placeholder="Full address of this branch"></textarea>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div className="form-group">
                  <label className="form-label">Branch GSTIN</label>
                  <input className="form-control" type="text" value={outletGstin} onChange={e => setOutletGstin(e.target.value.toUpperCase())} placeholder="Branch GSTIN" />
                </div>
                <div className="form-group">
                  <label className="form-label">Branch State</label>
                  <input className="form-control" type="text" value={outletState} onChange={e => setOutletState(e.target.value)} placeholder="e.g. Delhi" />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div className="form-group">
                  <label className="form-label">Branch Phone</label>
                  <input className="form-control" type="text" value={outletPhone} onChange={e => setOutletPhone(e.target.value)} placeholder="Phone number" />
                </div>
                <div className="form-group">
                  <label className="form-label">Branch Email</label>
                  <input className="form-control" type="email" value={outletEmail} onChange={e => setOutletEmail(e.target.value)} placeholder="branch@company.com" />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Default Pricing Tier</label>
                  <select className="form-control" value={outletPricingType} onChange={e => setOutletPricingType(e.target.value)}>
                    <option value="Base">Base Price (Base rate)</option>
                    <option value="SP1">SP1 ({sp1Label})</option>
                    <option value="SP2">SP2 ({sp2Label})</option>
                    <option value="SP3">SP3 ({sp3Label})</option>
                  </select>
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Branch UPI ID</label>
                  <input className="form-control" type="text" value={outletUpiId} onChange={e => setOutletUpiId(e.target.value)} placeholder="e.g. branch@okaxis" />
                </div>
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>{selectedOutletEdit ? 'Update Details' : 'Create Branch'}</button>
                {selectedOutletEdit && (
                  <button type="button" onClick={() => {
                    setSelectedOutletEdit(null);
                    setOutletName('');
                    setOutletLocation('');
                    setOutletPricingType('Base');
                    setOutletLogoUrl('');
                    setOutletAddress('');
                    setOutletGstin('');
                    setOutletState('');
                    setOutletPhone('');
                    setOutletEmail('');
                    setOutletUpiId('');
                  }} className="btn btn-secondary">Cancel</button>
                )}
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
