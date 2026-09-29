import { useEffect, useMemo, useState } from "react";
import { Routes, Route, Navigate, NavLink, useLocation, useNavigate } from "react-router-dom";
import {
  Alert, Avatar, Box, Button, Chip, CircularProgress, Dialog, DialogActions,
  DialogContent, DialogTitle, Divider, Drawer, IconButton, InputAdornment,
  List, ListItemButton, ListItemIcon, ListItemText, MenuItem, Paper,
  Snackbar, Stack, TextField, Toolbar, Tooltip, Typography
} from "@mui/material";
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import FlagRoundedIcon from "@mui/icons-material/FlagRounded";
import PublicRoundedIcon from "@mui/icons-material/PublicRounded";
import PeopleAltRoundedIcon from "@mui/icons-material/PeopleAltRounded";
import AnalyticsRoundedIcon from "@mui/icons-material/AnalyticsRounded";
import HistoryRoundedIcon from "@mui/icons-material/HistoryRounded";
import SettingsRoundedIcon from "@mui/icons-material/SettingsRounded";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import SearchRoundedIcon from "@mui/icons-material/SearchRounded";
import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import ShieldRoundedIcon from "@mui/icons-material/ShieldRounded";
import RocketLaunchRoundedIcon from "@mui/icons-material/RocketLaunchRounded";
import TuneRoundedIcon from "@mui/icons-material/TuneRounded";
import RefreshRoundedIcon from "@mui/icons-material/RefreshRounded";
import CheckCircleRoundedIcon from "@mui/icons-material/CheckCircleRounded";
import BlockRoundedIcon from "@mui/icons-material/BlockRounded";
import MenuRoundedIcon from "@mui/icons-material/MenuRounded";
import { api, endpoints, FeatureFlag, Environment } from "./api";

const nav = [
  { label: "Command Center", to: "/", icon: <DashboardRoundedIcon /> },
  { label: "Feature Flags", to: "/flags", icon: <FlagRoundedIcon /> },
  { label: "Environments", to: "/environments", icon: <PublicRoundedIcon /> },
  { label: "User Targeting", to: "/targeting", icon: <PeopleAltRoundedIcon /> },
  { label: "Analytics", to: "/analytics", icon: <AnalyticsRoundedIcon /> },
  { label: "Audit Trail", to: "/audit", icon: <HistoryRoundedIcon /> }
];

function useToast() {
  const [message, setMessage] = useState("");
  return { message, setMessage };
}

function App() {
  const [authed, setAuthed] = useState(Boolean(localStorage.getItem("access_token")));
  const toast = useToast();
  if (!authed) return <Login onLogin={() => setAuthed(true)} />;

  return (
    <>
      <Shell onLogout={() => { localStorage.clear(); setAuthed(false); }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/flags" element={<Flags toast={toast.setMessage} />} />
          <Route path="/environments" element={<Environments toast={toast.setMessage} />} />
          <Route path="/targeting" element={<Targeting toast={toast.setMessage} />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/audit" element={<Audit />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Shell>
      <Snackbar open={Boolean(toast.message)} autoHideDuration={3200} onClose={() => toast.setMessage("")}>
        <Alert severity="success" variant="filled">{toast.message}</Alert>
      </Snackbar>
    </>
  );
}

function Login({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("Admin@123");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit() {
    setBusy(true); setError("");
    try {
      const { data } = await api.post(endpoints.login, { email, password });
      const token = data.access_token || data.token;
      if (!token) throw new Error("No access token returned by the API");
      localStorage.setItem("access_token", token);
      onLogin();
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message || "Login failed");
    } finally { setBusy(false); }
  }

  return (
    <Box className="login-bg" sx={{ minHeight: "100vh", display: "grid", placeItems: "center", p: 3 }}>
      <Paper className="glass glow" sx={{ width: "min(460px,100%)", p: { xs: 3, sm: 5 }, borderRadius: 5 }}>
        <Stack spacing={3}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Box sx={{ width: 46, height: 46, borderRadius: 2.5, display: "grid", placeItems: "center", bgcolor: "primary.main", color: "#08070d" }}>
              <AutoAwesomeRoundedIcon />
            </Box>
            <Box>
              <Typography variant="h5">FlagVault</Typography>
              <Typography variant="caption" color="text.secondary">Feature Control Center</Typography>
            </Box>
          </Stack>
          <Box>
            <Typography variant="h4" sx={{ mb: 1 }}>Welcome back.</Typography>
            <Typography color="text.secondary">Control releases with precision, without redeploying.</Typography>
          </Box>
          {error && <Alert severity="error">{error}</Alert>}
          <TextField label="Email" value={email} onChange={e => setEmail(e.target.value)} fullWidth />
          <TextField label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} fullWidth />
          <Button size="large" variant="contained" onClick={submit} disabled={busy} startIcon={busy ? <CircularProgress size={18} /> : <ShieldRoundedIcon />}>
            {busy ? "Signing in…" : "Enter Control Center"}
          </Button>
          <Typography variant="caption" color="text.secondary" textAlign="center">
            Secure JWT authentication • Admin workspace
          </Typography>
        </Stack>
      </Paper>
    </Box>
  );
}

function Shell({ children, onLogout }: { children: React.ReactNode; onLogout: () => void }) {
  const [mobile, setMobile] = useState(false);
  const location = useLocation();
  const title = nav.find(n => n.to === location.pathname)?.label || "Command Center";

  const sidebar = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column", p: 2 }}>
      <Stack direction="row" spacing={1.5} alignItems="center" sx={{ p: 1.5, mb: 2 }}>
        <Box sx={{ width: 42, height: 42, borderRadius: 2.5, display: "grid", placeItems: "center", background: "linear-gradient(135deg,#a98cff,#5c43c7)", boxShadow: "0 10px 35px rgba(155,124,255,.28)" }}>
          <AutoAwesomeRoundedIcon />
        </Box>
        <Box>
          <Typography fontWeight={800}>FlagVault</Typography>
          <Typography variant="caption" color="text.secondary">CONTROL PLANE</Typography>
        </Box>
      </Stack>
      <Typography variant="overline" color="text.secondary" sx={{ px: 1.5, mb: 1 }}>Workspace</Typography>
      <List sx={{ px: .5 }}>
        {nav.map(item => (
          <NavLink key={item.to} to={item.to} onClick={() => setMobile(false)}>
            {({ isActive }) => (
              <ListItemButton selected={isActive} sx={{
                mb: .5, borderRadius: 2.5,
                "&.Mui-selected": { bgcolor: "rgba(155,124,255,.13)", color: "primary.main", border: "1px solid rgba(155,124,255,.12)" },
                "&.Mui-selected:hover": { bgcolor: "rgba(155,124,255,.18)" }
              }}>
                <ListItemIcon sx={{ minWidth: 38, color: isActive ? "primary.main" : "text.secondary" }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: 14, fontWeight: isActive ? 750 : 550 }} />
              </ListItemButton>
            )}
          </NavLink>
        ))}
      </List>
      <Box sx={{ flex: 1 }} />
      <Paper className="glass" sx={{ p: 1.5, borderRadius: 3, mb: 1.5 }}>
        <Stack direction="row" spacing={1.2} alignItems="center">
          <Avatar sx={{ width: 34, height: 34, bgcolor: "rgba(88,214,196,.16)", color: "secondary.main" }}>A</Avatar>
          <Box sx={{ minWidth: 0, flex: 1 }}>
            <Typography fontSize={13} fontWeight={700}>Administrator</Typography>
            <Typography fontSize={11} color="text.secondary" noWrap>admin@example.com</Typography>
          </Box>
          <Tooltip title="Sign out"><IconButton size="small" onClick={onLogout}><LogoutRoundedIcon fontSize="small" /></IconButton></Tooltip>
        </Stack>
      </Paper>
    </Box>
  );

  return (
    <Box sx={{ minHeight: "100vh", display: "flex" }}>
      <Box component="aside" sx={{ display: { xs: "none", md: "block" }, width: 260, flexShrink: 0, borderRight: "1px solid rgba(255,255,255,.06)", position: "sticky", top: 0, height: "100vh" }}>
        {sidebar}
      </Box>
      <Drawer open={mobile} onClose={() => setMobile(false)} sx={{ display: { md: "none" } }} PaperProps={{ sx: { width: 280, bgcolor: "#0b0b12" } }}>{sidebar}</Drawer>
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Toolbar sx={{ px: { xs: 2, md: 4 }, borderBottom: "1px solid rgba(255,255,255,.06)", bgcolor: "rgba(7,7,11,.72)", backdropFilter: "blur(18px)", position: "sticky", top: 0, zIndex: 10 }}>
          <IconButton sx={{ display: { md: "none" }, mr: 1 }} onClick={() => setMobile(true)}><MenuRoundedIcon /></IconButton>
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" color="text.secondary">FEATURE CONTROL / {title.toUpperCase()}</Typography>
            <Typography fontWeight={800}>{title}</Typography>
          </Box>
          <Chip icon={<RocketLaunchRoundedIcon />} label="LIVE CONTROL PLANE" size="small" sx={{ bgcolor: "rgba(84,211,138,.09)", color: "success.main", border: "1px solid rgba(84,211,138,.16)" }} />
        </Toolbar>
        <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1600, mx: "auto" }}>{children}</Box>
      </Box>
    </Box>
  );
}

function PageHead({ eyebrow, title, subtitle, action }: any) {
  return (
    <Stack direction={{ xs: "column", md: "row" }} spacing={2} justifyContent="space-between" alignItems={{ md: "flex-end" }} sx={{ mb: 3 }}>
      <Box>
        <Typography variant="overline" color="primary.main">{eyebrow}</Typography>
        <Typography variant="h4">{title}</Typography>
        <Typography color="text.secondary" sx={{ mt: .5 }}>{subtitle}</Typography>
      </Box>
      {action}
    </Stack>
  );
}

function StatCard({ icon, label, value, hint }: any) {
  return (
    <Paper className="glass" sx={{ p: 2.3, borderRadius: 3.5, height: "100%" }}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Box sx={{ width: 42, height: 42, borderRadius: 2.2, display: "grid", placeItems: "center", bgcolor: "rgba(155,124,255,.11)", color: "primary.main" }}>{icon}</Box>
        <Typography variant="caption" color="text.secondary">{hint}</Typography>
      </Stack>
      <Typography variant="h4" sx={{ mt: 2 }}>{value}</Typography>
      <Typography color="text.secondary" fontSize={13}>{label}</Typography>
    </Paper>
  );
}

function Dashboard() {
  const [data, setData] = useState<any>({});
  const [flags, setFlags] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [s, f] = await Promise.all([
        api.get(endpoints.summary),
        api.get(endpoints.flags)
      ]);
      setData(s.data || {});
      setFlags(Array.isArray(f.data) ? f.data : f.data?.items || []);
    } catch {}
    finally { setLoading(false); }
  }
  useEffect(() => { load(); }, []);

  const total = data.total_features ?? data.total_flags ?? flags.length;
  const enabled = data.enabled_features ?? data.enabled_flags ?? flags.filter(f => f.default_enabled).length;
  const envs = data.total_environments ?? data.environments ?? "—";
  const users = data.total_users ?? data.users ?? "—";

  return (
    <>
      <PageHead eyebrow="Command Center" title="Release intelligence, at a glance." subtitle="A premium control plane for safer feature delivery." action={<Button startIcon={<RefreshRoundedIcon />} onClick={load}>Refresh</Button>} />
      {loading ? <CircularProgress /> : (
        <>
          <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "repeat(2,1fr)", xl: "repeat(4,1fr)" }, gap: 2, mb: 3 }}>
            <StatCard icon={<FlagRoundedIcon />} label="Feature flags" value={total} hint="TOTAL" />
            <StatCard icon={<CheckCircleRoundedIcon />} label="Enabled flags" value={enabled} hint="ACTIVE" />
            <StatCard icon={<PublicRoundedIcon />} label="Environments" value={envs} hint="SCOPES" />
            <StatCard icon={<PeopleAltRoundedIcon />} label="Users" value={users} hint="AUDIENCE" />
          </Box>
          <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", lg: "1.5fr 1fr" }, gap: 2 }}>
            <Paper className="glass" sx={{ p: 2.5, borderRadius: 4 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Box><Typography fontWeight={800}>Feature registry</Typography><Typography variant="caption" color="text.secondary">Latest control-plane inventory</Typography></Box>
                <Chip label={`${flags.length} flags`} size="small" />
              </Stack>
              <Stack spacing={1}>
                {flags.slice(0, 6).map(f => (
                  <Stack key={f.id} direction="row" alignItems="center" spacing={1.5} sx={{ p: 1.2, borderRadius: 2.5, bgcolor: "rgba(255,255,255,.025)" }}>
                    <Box sx={{ width: 8, height: 8, borderRadius: "50%", bgcolor: f.default_enabled ? "success.main" : "text.secondary", boxShadow: f.default_enabled ? "0 0 14px rgba(84,211,138,.6)" : "none" }} />
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography fontWeight={700} fontSize={14}>{f.name}</Typography>
                      <Typography className="mono" fontSize={11} color="text.secondary">{f.key}</Typography>
                    </Box>
                    <Chip size="small" label={f.default_enabled ? "ON" : "OFF"} color={f.default_enabled ? "success" : "default"} />
                  </Stack>
                ))}
                {!flags.length && <Typography color="text.secondary">No feature flags yet.</Typography>}
              </Stack>
            </Paper>
            <Paper className="glass glow" sx={{ p: 3, borderRadius: 4, position: "relative", overflow: "hidden" }}>
              <Box sx={{ position: "absolute", width: 220, height: 220, borderRadius: "50%", bgcolor: "rgba(155,124,255,.08)", filter: "blur(30px)", top: -100, right: -60 }} />
              <Stack spacing={2.5} sx={{ position: "relative" }}>
                <Chip icon={<AutoAwesomeRoundedIcon />} label="Release posture" sx={{ width: "fit-content" }} />
                <Typography variant="h5">Ship with confidence.</Typography>
                <Typography color="text.secondary">Control activation by environment, percentage and user targeting — all from one workspace.</Typography>
                <Stack spacing={1.2}>
                  {["No redeploy required", "JWT + role-aware APIs", "Rollback-ready releases"].map(t => <Stack key={t} direction="row" spacing={1} alignItems="center"><CheckCircleRoundedIcon sx={{ color: "secondary.main", fontSize: 18 }} /><Typography fontSize={13}>{t}</Typography></Stack>)}
                </Stack>
              </Stack>
            </Paper>
          </Box>
        </>
      )}
    </>
  );
}

function Flags({ toast }: { toast: (s: string) => void }) {
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<FeatureFlag | null>(null);
  const [form, setForm] = useState({ name: "", key: "", description: "", default_enabled: false });

  async function load() { const r = await api.get(endpoints.flags); setFlags(Array.isArray(r.data) ? r.data : r.data?.items || []); }
  useEffect(() => { load().catch(() => {}); }, []);
  const filtered = useMemo(() => flags.filter(f => `${f.name} ${f.key}`.toLowerCase().includes(search.toLowerCase())), [flags, search]);

  function startCreate() { setEditing(null); setForm({ name: "", key: "", description: "", default_enabled: false }); setOpen(true); }
  function startEdit(f: FeatureFlag) { setEditing(f); setForm({ name: f.name, key: f.key, description: f.description || "", default_enabled: Boolean(f.default_enabled) }); setOpen(true); }

  async function save() {
    if (editing) await api.patch(`${endpoints.flags}/${editing.id}`, form);
    else await api.post(endpoints.flags, form);
    setOpen(false); await load(); toast(editing ? "Feature flag updated" : "Feature flag created");
  }

  async function remove(id: number) { await api.delete(`${endpoints.flags}/${id}`); await load(); toast("Feature flag archived"); }

  return (
    <>
      <PageHead eyebrow="Control Plane" title="Feature Flags" subtitle="Design, activate and retire product capabilities." action={<Button variant="contained" startIcon={<AddRoundedIcon />} onClick={startCreate}>New flag</Button>} />
      <Paper className="glass" sx={{ p: 1.5, borderRadius: 3, mb: 2 }}>
        <TextField fullWidth placeholder="Search by name or key…" value={search} onChange={e => setSearch(e.target.value)} InputProps={{ startAdornment: <InputAdornment position="start"><SearchRoundedIcon /></InputAdornment> }} />
      </Paper>
      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "repeat(2,1fr)", xl: "repeat(3,1fr)" }, gap: 2 }}>
        {filtered.map(f => (
          <Paper key={f.id} className="glass" sx={{ p: 2.5, borderRadius: 4 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
              <Box sx={{ width: 44, height: 44, borderRadius: 2.5, display: "grid", placeItems: "center", bgcolor: "rgba(155,124,255,.1)", color: "primary.main" }}><FlagRoundedIcon /></Box>
              <Chip size="small" label={f.default_enabled ? "Enabled" : "Disabled"} color={f.default_enabled ? "success" : "default"} />
            </Stack>
            <Typography variant="h6" sx={{ mt: 2, fontWeight: 800 }}>{f.name}</Typography>
            <Typography className="mono" fontSize={12} color="primary.main">{f.key}</Typography>
            <Typography color="text.secondary" fontSize={13} sx={{ mt: 1.5, minHeight: 40 }}>{f.description || "No description provided."}</Typography>
            <Divider sx={{ my: 2, borderColor: "rgba(255,255,255,.07)" }} />
            <Stack direction="row" spacing={1}>
              <Button size="small" variant="outlined" onClick={() => startEdit(f)}>Edit</Button>
              <Button size="small" color="error" onClick={() => remove(f.id)}>Delete</Button>
            </Stack>
          </Paper>
        ))}
      </Box>
      {!filtered.length && <Paper className="glass" sx={{ p: 5, textAlign: "center", mt: 2 }}><Typography color="text.secondary">No matching feature flags.</Typography></Paper>}
      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editing ? "Edit feature flag" : "Create feature flag"}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <TextField label="Name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
            <TextField label="Key" value={form.key} onChange={e => setForm({ ...form, key: e.target.value })} />
            <TextField label="Description" multiline rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
            <TextField select label="Default state" value={String(form.default_enabled)} onChange={e => setForm({ ...form, default_enabled: e.target.value === "true" })}>
              <MenuItem value="false">Disabled</MenuItem><MenuItem value="true">Enabled</MenuItem>
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions><Button onClick={() => setOpen(false)}>Cancel</Button><Button variant="contained" onClick={save}>Save flag</Button></DialogActions>
      </Dialog>
    </>
  );
}

function Environments({ toast }: { toast: (s: string) => void }) {
  const [items, setItems] = useState<Environment[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  async function load() { const r = await api.get(endpoints.environments); setItems(Array.isArray(r.data) ? r.data : r.data?.items || []); }
  useEffect(() => { load().catch(() => {}); }, []);

  async function create() {
    await api.post(endpoints.environments, { name, description });
    setName(""); setDescription(""); await load(); toast("Environment created");
  }

  return (
    <>
      <PageHead eyebrow="Release Scope" title="Environments" subtitle="Keep development, testing and production activation isolated." />
      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", lg: "1.4fr 1fr" }, gap: 2 }}>
        <Stack spacing={2}>
          {items.map((e, i) => (
            <Paper key={e.id} className="glass" sx={{ p: 2.5, borderRadius: 4 }}>
              <Stack direction="row" spacing={2} alignItems="center">
                <Box sx={{ width: 48, height: 48, borderRadius: 2.5, display: "grid", placeItems: "center", bgcolor: i === 2 ? "rgba(255,107,134,.1)" : "rgba(88,214,196,.1)", color: i === 2 ? "error.main" : "secondary.main" }}><PublicRoundedIcon /></Box>
                <Box sx={{ flex: 1 }}><Typography variant="h6" fontWeight={800}>{e.name}</Typography><Typography color="text.secondary" fontSize={13}>{e.description || "Deployment environment"}</Typography></Box>
                <Chip label="Active" color="success" size="small" />
              </Stack>
            </Paper>
          ))}
          {!items.length && <Paper className="glass" sx={{ p: 4 }}><Typography color="text.secondary">No environments found.</Typography></Paper>}
        </Stack>
        <Paper className="glass" sx={{ p: 3, borderRadius: 4 }}>
          <Typography variant="h6" fontWeight={800}>Add environment</Typography>
          <Typography color="text.secondary" fontSize={13} sx={{ mb: 2 }}>Create an additional release scope.</Typography>
          <Stack spacing={2}>
            <TextField label="Name" value={name} onChange={e => setName(e.target.value)} placeholder="staging" />
            <TextField label="Description" value={description} onChange={e => setDescription(e.target.value)} multiline rows={3} />
            <Button variant="contained" startIcon={<AddRoundedIcon />} onClick={create} disabled={!name}>Create environment</Button>
          </Stack>
        </Paper>
      </Box>
    </>
  );
}

function Targeting({ toast }: { toast: (s: string) => void }) {
  const [flagId, setFlagId] = useState("2");
  const [assignments, setAssignments] = useState<any[]>([]);
  const [userId, setUserId] = useState("1");
  const [enabled, setEnabled] = useState(true);
  const [reason, setReason] = useState("Beta user access");

  async function load() {
    const r = await api.get(endpoints.assignments(Number(flagId)));
    setAssignments(Array.isArray(r.data) ? r.data : []);
  }
  async function add() {
    await api.post(endpoints.assignments(Number(flagId)), { user_id: Number(userId), enabled, reason });
    await load(); toast("User assignment created");
  }
  async function remove(id: number) {
    await api.delete(endpoints.assignment(Number(flagId), id));
    await load(); toast("Assignment removed");
  }

  return (
    <>
      <PageHead eyebrow="Audience Control" title="User Targeting" subtitle="Override rollout behavior for specific users." action={<Button onClick={() => load()} startIcon={<RefreshRoundedIcon />}>Refresh</Button>} />
      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", lg: "1fr 1.5fr" }, gap: 2 }}>
        <Paper className="glass" sx={{ p: 3, borderRadius: 4 }}>
          <Stack spacing={2}>
            <TextField label="Feature flag ID" value={flagId} onChange={e => setFlagId(e.target.value)} />
            <TextField label="User ID" value={userId} onChange={e => setUserId(e.target.value)} />
            <TextField select label="Assignment" value={String(enabled)} onChange={e => setEnabled(e.target.value === "true")}>
              <MenuItem value="true">Enable feature</MenuItem><MenuItem value="false">Disable feature</MenuItem>
            </TextField>
            <TextField label="Reason" value={reason} onChange={e => setReason(e.target.value)} />
            <Button variant="contained" startIcon={<AddRoundedIcon />} onClick={add}>Assign user</Button>
            <Button variant="outlined" onClick={load}>Load assignments</Button>
          </Stack>
        </Paper>
        <Paper className="glass" sx={{ p: 2.5, borderRadius: 4 }}>
          <Typography fontWeight={800} sx={{ mb: 2 }}>Assignments</Typography>
          <Stack spacing={1}>
            {assignments.map(a => (
              <Stack key={a.id} direction="row" alignItems="center" spacing={1.5} sx={{ p: 1.5, borderRadius: 2.5, bgcolor: "rgba(255,255,255,.025)" }}>
                <Avatar sx={{ width: 36, height: 36, bgcolor: a.enabled ? "rgba(84,211,138,.12)" : "rgba(255,107,134,.12)", color: a.enabled ? "success.main" : "error.main" }}>{a.user_id}</Avatar>
                <Box sx={{ flex: 1 }}><Typography fontWeight={700}>User {a.user_id}</Typography><Typography variant="caption" color="text.secondary">{a.reason || "No reason"}</Typography></Box>
                <Chip size="small" label={a.enabled ? "Enabled" : "Disabled"} color={a.enabled ? "success" : "error"} />
                <IconButton size="small" onClick={() => remove(a.id)}><BlockRoundedIcon fontSize="small" /></IconButton>
              </Stack>
            ))}
            {!assignments.length && <Typography color="text.secondary" sx={{ p: 3, textAlign: "center" }}>No assignments for this flag.</Typography>}
          </Stack>
        </Paper>
      </Box>
    </>
  );
}

function Analytics() {
  const [flagId, setFlagId] = useState("2");
  const [data, setData] = useState<any>({});
  const [top, setTop] = useState<any[]>([]);
  async function load() {
    const [a, t] = await Promise.all([
      api.get(endpoints.analytics(Number(flagId))),
      api.get(endpoints.topFlags)
    ]);
    setData(a.data || {});
    setTop(Array.isArray(t.data) ? t.data : []);
  }
  useEffect(() => { load().catch(() => {}); }, []);

  const values = [
    { name: "Enabled", value: Number(data.enabled_evaluations || 0) },
    { name: "Disabled", value: Number(data.disabled_evaluations || 0) }
  ];

  return (
    <>
      <PageHead eyebrow="Observability" title="Analytics" subtitle="Understand how your feature controls are being evaluated." action={<Stack direction="row" spacing={1}><TextField label="Flag ID" value={flagId} onChange={e => setFlagId(e.target.value)} /><Button variant="contained" onClick={() => load()}>Inspect</Button></Stack>} />
      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "repeat(3,1fr)" }, gap: 2, mb: 2 }}>
        <StatCard icon={<AnalyticsRoundedIcon />} label="Evaluations" value={data.evaluations ?? 0} hint="TOTAL" />
        <StatCard icon={<CheckCircleRoundedIcon />} label="Enabled evaluations" value={data.enabled_evaluations ?? 0} hint="ON" />
        <StatCard icon={<BlockRoundedIcon />} label="Disabled evaluations" value={data.disabled_evaluations ?? 0} hint="OFF" />
      </Box>
      <Paper className="glass" sx={{ p: 3, borderRadius: 4 }}>
        <Typography fontWeight={800} sx={{ mb: 2 }}>Top flags</Typography>
        {top.length ? top.map((x, i) => <Stack key={i} direction="row" spacing={2} alignItems="center" sx={{ py: 1.2 }}><Typography className="mono" color="primary.main">{i+1}</Typography><Typography sx={{ flex: 1 }}>{x.name || x.key || x.feature_key || `Flag ${x.feature_flag_id}`}</Typography><Typography color="text.secondary">{x.evaluations ?? x.count ?? 0} evaluations</Typography></Stack>) : <Typography color="text.secondary">No usage records have been returned yet.</Typography>}
      </Paper>
    </>
  );
}

function Audit() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  async function load() {
    setLoading(true);
    try {
      const r = await api.get(endpoints.audit);
      setLogs(Array.isArray(r.data) ? r.data : r.data?.items || []);
    } finally { setLoading(false); }
  }
  useEffect(() => { load().catch(() => {}); }, []);

  return (
    <>
      <PageHead eyebrow="Governance" title="Audit Trail" subtitle="A chronological record of control-plane changes." action={<Button startIcon={<RefreshRoundedIcon />} onClick={() => load()}>Refresh</Button>} />
      <Paper className="glass" sx={{ p: 2.5, borderRadius: 4 }}>
        {loading ? <CircularProgress /> : logs.length ? (
          <Stack spacing={1}>
            {logs.map((l, i) => (
              <Stack key={l.id || i} direction="row" spacing={2} alignItems="flex-start" sx={{ p: 1.5, borderBottom: "1px solid rgba(255,255,255,.05)" }}>
                <Box sx={{ mt: .5, width: 10, height: 10, borderRadius: "50%", bgcolor: "primary.main", boxShadow: "0 0 14px rgba(155,124,255,.5)" }} />
                <Box sx={{ flex: 1 }}><Typography fontWeight={700}>{l.action || l.event || "Change recorded"}</Typography><Typography variant="caption" color="text.secondary">{l.entity_type || "system"} {l.entity_id ? `#${l.entity_id}` : ""}</Typography></Box>
                <Typography variant="caption" color="text.secondary">{l.created_at || l.timestamp || ""}</Typography>
              </Stack>
            ))}
          </Stack>
        ) : <Box sx={{ p: 5, textAlign: "center" }}><HistoryRoundedIcon sx={{ fontSize: 42, color: "text.secondary" }} /><Typography sx={{ mt: 1 }} color="text.secondary">No audit records returned.</Typography></Box>}
      </Paper>
    </>
  );
}

export default App;
