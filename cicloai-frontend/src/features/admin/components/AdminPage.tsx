import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Drawer,
  FormControlLabel,
  IconButton,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TablePagination,
  TableRow,
  TableSortLabel,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import ArrowBackOutlinedIcon from '@mui/icons-material/ArrowBackOutlined';
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined';
import CategoryOutlinedIcon from '@mui/icons-material/CategoryOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import CloseOutlinedIcon from '@mui/icons-material/CloseOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import DirectionsBikeOutlinedIcon from '@mui/icons-material/DirectionsBikeOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';
import FlagOutlinedIcon from '@mui/icons-material/FlagOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined';
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import RadioButtonUncheckedOutlinedIcon from '@mui/icons-material/RadioButtonUncheckedOutlined';
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import { BrandMark } from '@/components/common/BrandMark';
import { FullScreenFlowLayout } from '@/components/layout/FullScreenFlowLayout';
import { adminAuthService } from '@/features/admin/services/adminAuthService';
import {
  AdminBiker,
  AdminBikerPayload,
  AdminCategory,
  AdminCategoryPayload,
  AdminDashboard,
  AdminPayment,
  AdminRace,
  AdminRacePayload,
  BikerExportField,
  BikerGender,
  BikerSortBy,
  BikerStatus,
  CategorySex,
  CategoryType,
  RaceStatus,
  SortDirection,
  adminService,
} from '@/features/admin/services/adminService';
import { adminTokenStorage } from '@/features/admin/services/adminTokenStorage';

const emptyRaceForm: AdminRacePayload = {
  name: '',
  location_name: '',
  location: '',
  strava_map_html: '',
  year: new Date().getFullYear(),
  date_of_race: null,
  status: 'deactive',
  cost: 0,
  currency: 'BOB',
};

const emptyCategoryForm: AdminCategoryPayload = {
  name: '',
  category_type: 'Federado',
  sex: 'varones',
  age_from: 0,
  age_to: null,
  born_from: new Date().getFullYear(),
  born_to: new Date().getFullYear(),
  race_ids: [],
};

const bikerExportOptions: Array<{ field: BikerExportField; label: string }> = [
  { field: 'full_name', label: 'Nombre Completo' },
  { field: 'gender', label: 'Sexo' },
  { field: 'detected_category', label: 'Categoría' },
  { field: 'age', label: 'Edad' },
  { field: 'bike_team_name', label: 'Club de Ciclismo' },
];

function toRaceForm(race: AdminRace): AdminRacePayload {
  return {
    name: race.name,
    location_name: race.location_name,
    location: race.location,
    strava_map_html: race.strava_map_html,
    year: race.year,
    date_of_race: race.date_of_race,
    status: race.status,
    cost: Number(race.cost),
    currency: race.currency,
  };
}

function toCategoryForm(category: AdminCategory): AdminCategoryPayload {
  return {
    name: category.name,
    category_type: category.category_type,
    sex: category.sex,
    age_from: category.age_from,
    age_to: category.age_to,
    born_from: category.born_from,
    born_to: category.born_to,
    race_ids: category.race_ids,
  };
}

function toBikerForm(biker: AdminBiker): AdminBikerPayload {
  return {
    full_name: biker.full_name,
    email: biker.email,
    dni: biker.dni,
    dni_extension: biker.dni_extension,
    birth_date: biker.birth_date,
    gender: biker.gender,
    requested_category: biker.requested_category,
    detected_category: biker.detected_category,
    bike_team_name: biker.bike_team_name,
    payment_status: biker.payment_status,
    payment_reference: biker.payment_reference,
    status: biker.status,
  };
}

function statusIcon(status: BikerStatus) {
  if (status === 'habilitado') {
    return <CheckCircleOutlineIcon color="success" fontSize="small" />;
  }
  if (status === 'deshabilitado') {
    return <CancelOutlinedIcon color="error" fontSize="small" />;
  }
  return <RadioButtonUncheckedOutlinedIcon color="disabled" fontSize="small" />;
}

function bikerStatusChipColor(status: BikerStatus): 'success' | 'error' | 'default' {
  if (status === 'habilitado') {
    return 'success';
  }
  if (status === 'deshabilitado') {
    return 'error';
  }
  return 'default';
}

function genderIconColor(gender: BikerGender): string {
  return gender === 'hombre' ? '#1976d2' : '#d81b60';
}

function toUpperText(value: string): string {
  return value.trim().toUpperCase();
}

function genderTooltip(gender: BikerGender): string {
  return gender === 'hombre' ? 'Hombre' : 'Mujer';
}

function formatMoney(value: string | number | null | undefined, currency: string): string {
  if (value === null || value === undefined || value === '') {
    return '-';
  }
  return `${Number(value).toFixed(2)} ${currency}`;
}

type AdminSection = 'dashboard' | 'races' | 'payments' | 'categories';
type AdminWorkView = 'races-table' | 'race-edit' | 'bikers-table' | 'biker-edit' | 'categories-table' | 'category-edit';

export function AdminPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [sessionUsername, setSessionUsername] = useState<string | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [section, setSection] = useState<AdminSection>('dashboard');
  const [dashboard, setDashboard] = useState<AdminDashboard | null>(null);
  const [races, setRaces] = useState<AdminRace[]>([]);
  const [categories, setCategories] = useState<AdminCategory[]>([]);
  const [selectedRace, setSelectedRace] = useState<AdminRace | null>(null);
  const [selectedPaymentRace, setSelectedPaymentRace] = useState<AdminRace | null>(null);
  const [mapPreviewRace, setMapPreviewRace] = useState<AdminRace | null>(null);
  const [bikers, setBikers] = useState<AdminBiker[]>([]);
  const [payments, setPayments] = useState<AdminPayment[]>([]);
  const [raceForm, setRaceForm] = useState<AdminRacePayload>(emptyRaceForm);
  const [categoryForm, setCategoryForm] = useState<AdminCategoryPayload>(emptyCategoryForm);
  const [editingRaceId, setEditingRaceId] = useState<string | null>(null);
  const [editingCategoryId, setEditingCategoryId] = useState<string | null>(null);
  const [editingBiker, setEditingBiker] = useState<AdminBiker | null>(null);
  const [bikerForm, setBikerForm] = useState<AdminBikerPayload | null>(null);
  const [workView, setWorkView] = useState<AdminWorkView>('races-table');
  const [raceSearch, setRaceSearch] = useState('');
  const [bikerSearch, setBikerSearch] = useState('');
  const [racePage, setRacePage] = useState(0);
  const [bikerPage, setBikerPage] = useState(0);
  const [bikerTotal, setBikerTotal] = useState(0);
  const [bikerSortBy, setBikerSortBy] = useState<BikerSortBy>('created_at');
  const [bikerSortDirection, setBikerSortDirection] = useState<SortDirection>('desc');
  const [bikerExportOpen, setBikerExportOpen] = useState(false);
  const [bikerExportFields, setBikerExportFields] = useState<BikerExportField[]>([
    'full_name',
    'gender',
    'detected_category',
    'age',
    'bike_team_name',
  ]);
  const [pendingStatusChange, setPendingStatusChange] = useState<{ biker: AdminBiker; status: BikerStatus } | null>(null);
  const [proofPreviewUrl, setProofPreviewUrl] = useState<string | null>(null);

  const activeRace = useMemo(() => races.find((race) => race.status === 'active') ?? null, [races]);
  const filteredRaces = useMemo(() => {
    const search = raceSearch.trim().toUpperCase();
    if (!search) {
      return races;
    }

    return races.filter((race) =>
      [race.name, race.location_name, race.location ?? '', String(race.year), race.status].some((value) =>
        value.toUpperCase().includes(search),
      ),
    );
  }, [raceSearch, races]);
  const paginatedRaces = useMemo(() => filteredRaces.slice(racePage * 10, racePage * 10 + 10), [filteredRaces, racePage]);
  const selectedRacePayments = useMemo(
    () => payments.filter((payment) => payment.race_id === selectedPaymentRace?.id),
    [payments, selectedPaymentRace?.id],
  );
  const refreshAdminData = useCallback(async () => {
    const [dashboardResponse, racesResponse, categoriesResponse] = await Promise.all([
      adminService.dashboard(),
      adminService.listRaces(),
      adminService.listCategories(),
    ]);
    setDashboard(dashboardResponse);
    setRaces(racesResponse);
    setCategories(categoriesResponse);
  }, []);

  const loadPayments = useCallback(async () => {
    setPayments(await adminService.listPayments());
  }, []);

  const loadBikers = useCallback(async (
    race: AdminRace,
    options?: Partial<{ page: number; search: string; sortBy: BikerSortBy; sortDirection: SortDirection; resetSearch: boolean }>,
  ) => {
    const nextPage = options?.page ?? bikerPage;
    const nextSearch = options?.resetSearch ? '' : options?.search ?? bikerSearch;
    const nextSortBy = options?.sortBy ?? bikerSortBy;
    const nextSortDirection = options?.sortDirection ?? bikerSortDirection;
    const response = await adminService.listBikers(race.id, {
      page: nextPage,
      pageSize: 50,
      search: nextSearch,
      sortBy: nextSortBy,
      sortDirection: nextSortDirection,
    });
    setSelectedRace(race);
    setBikers(response.items);
    setBikerTotal(response.total);
    setBikerSearch(nextSearch);
    setBikerPage(response.page);
    setBikerSortBy(nextSortBy);
    setBikerSortDirection(nextSortDirection);
    setWorkView('bikers-table');
  }, [bikerPage, bikerSearch, bikerSortBy, bikerSortDirection]);

  useEffect(() => {
    const token = adminTokenStorage.get();
    if (!token) {
      setCheckingSession(false);
      return;
    }

    adminAuthService
      .me(token)
      .then(async (session) => {
        setSessionUsername(session.username);
        await refreshAdminData();
        await loadPayments();
      })
      .catch(() => {
        adminTokenStorage.clear();
      })
      .finally(() => {
        setCheckingSession(false);
      });
  }, [loadPayments, refreshAdminData]);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await adminAuthService.login({ username, password });
      adminTokenStorage.set(response.access_token);
      setSessionUsername(response.username);
      setPassword('');
      await refreshAdminData();
      await loadPayments();
    } catch (loginError) {
      setError(loginError instanceof Error ? loginError.message : 'No se pudo iniciar sesión.');
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    adminTokenStorage.clear();
    setSessionUsername(null);
    setUsername('');
    setPassword('');
    setDashboard(null);
    setRaces([]);
    setCategories([]);
    setSelectedRace(null);
    setSelectedPaymentRace(null);
    setMapPreviewRace(null);
    setBikers([]);
    setPayments([]);
    setBikerTotal(0);
    setBikerSearch('');
    setBikerPage(0);
    setWorkView('races-table');
    setEditingCategoryId(null);
    setCategoryForm(emptyCategoryForm);
    setPendingStatusChange(null);
    setProofPreviewUrl(null);
    setError(null);
  }

  async function handleRaceSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const otherActiveRace = activeRace && activeRace.id !== editingRaceId;
    if (raceForm.status === 'active' && otherActiveRace) {
      setError('Solo puede existir una carrera activa. Desactiva la carrera activa antes de continuar.');
      setLoading(false);
      return;
    }

    const payload = {
      ...raceForm,
      location: raceForm.location?.trim() ? raceForm.location.trim() : null,
      strava_map_html: raceForm.strava_map_html?.trim() ? raceForm.strava_map_html.trim() : null,
      date_of_race: raceForm.date_of_race || null,
      cost: Number(raceForm.cost),
      year: Number(raceForm.year),
    };

    try {
      if (editingRaceId) {
        await adminService.updateRace(editingRaceId, payload);
      } else {
        await adminService.createRace(payload);
      }
      setRaceForm(emptyRaceForm);
      setEditingRaceId(null);
      await refreshAdminData();
      setWorkView('races-table');
    } catch (raceError) {
      setError(raceError instanceof Error ? raceError.message : 'No se pudo guardar la carrera.');
    } finally {
      setLoading(false);
    }
  }

  async function handleDeactivateRace(race: AdminRace) {
    setLoading(true);
    setError(null);
    try {
      await adminService.deactivateRace(race.id);
      await refreshAdminData();
    } catch (raceError) {
      setError(raceError instanceof Error ? raceError.message : 'No se pudo desactivar la carrera.');
    } finally {
      setLoading(false);
    }
  }

  async function handleCategorySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (editingCategoryId) {
        await adminService.updateCategory(editingCategoryId, categoryForm);
      } else {
        await adminService.createCategory(categoryForm);
      }
      setCategoryForm(emptyCategoryForm);
      setEditingCategoryId(null);
      await refreshAdminData();
      setWorkView('categories-table');
    } catch (categoryError) {
      setError(categoryError instanceof Error ? categoryError.message : 'No se pudo guardar la categoría.');
    } finally {
      setLoading(false);
    }
  }

  async function handleCategoryStatus(category: AdminCategory, status: 'active' | 'deactive') {
    setLoading(true);
    setError(null);
    try {
      await adminService.updateCategoryStatus(category.id, status);
      await refreshAdminData();
    } catch (categoryError) {
      setError(categoryError instanceof Error ? categoryError.message : 'No se pudo actualizar la categoría.');
    } finally {
      setLoading(false);
    }
  }

  async function handleBikerStatus(biker: AdminBiker, status: BikerStatus) {
    setLoading(true);
    setError(null);
    try {
      await adminService.updateBikerStatus(biker.id, status);
      setPendingStatusChange(null);
      if (selectedRace) {
        await loadBikers(selectedRace, { page: bikerPage });
      }
      await refreshAdminData();
    } catch (statusError) {
      setError(statusError instanceof Error ? statusError.message : 'No se pudo actualizar el estado.');
    } finally {
      setLoading(false);
    }
  }

  async function handleBikerSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editingBiker || !bikerForm) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await adminService.updateBiker(editingBiker.id, bikerForm);
      setEditingBiker(null);
      setBikerForm(null);
      if (selectedRace) {
        await loadBikers(selectedRace, { page: bikerPage });
      }
      await refreshAdminData();
      setWorkView('bikers-table');
    } catch (bikerError) {
      setError(bikerError instanceof Error ? bikerError.message : 'No se pudo actualizar el corredor.');
    } finally {
      setLoading(false);
    }
  }

  async function handleOpenProofUrl(paymentProofUrl: string | null) {
    if (!paymentProofUrl) {
      return;
    }

    try {
      if (proofPreviewUrl) {
        window.URL.revokeObjectURL(proofPreviewUrl);
      }
      setProofPreviewUrl(await adminService.loadPaymentProof(paymentProofUrl));
    } catch (proofError) {
      setError(proofError instanceof Error ? proofError.message : 'No se pudo abrir el comprobante.');
    }
  }

  async function handleOpenProof(biker: AdminBiker) {
    await handleOpenProofUrl(biker.payment_proof_url);
  }

  async function handleValidatePayment(payment: AdminPayment) {
    setLoading(true);
    setError(null);
    try {
      await adminService.validatePayment(payment.id);
      await loadPayments();
      await refreshAdminData();
    } catch (paymentError) {
      setError(paymentError instanceof Error ? paymentError.message : 'No se pudo validar el pago.');
    } finally {
      setLoading(false);
    }
  }

  async function handleExportBikers() {
    if (!selectedRace) {
      return;
    }
    if (bikerExportFields.length === 0) {
      setError('Selecciona al menos una columna para exportar.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await adminService.exportBikersExcel(selectedRace.id, bikerExportFields);
      setBikerExportOpen(false);
    } catch (exportError) {
      setError(exportError instanceof Error ? exportError.message : 'No se pudo exportar corredores.');
    } finally {
      setLoading(false);
    }
  }

  function handleCloseProofPreview() {
    if (proofPreviewUrl) {
      window.URL.revokeObjectURL(proofPreviewUrl);
    }
    setProofPreviewUrl(null);
  }

  if (checkingSession) {
    return (
      <FullScreenFlowLayout maxWidth="sm">
        <Stack sx={{ height: '100%', justifyContent: 'center' }} spacing={3}>
          <BrandMark />
          <Typography color="text.secondary">Validando sesión...</Typography>
        </Stack>
      </FullScreenFlowLayout>
    );
  }

  if (!sessionUsername) {
    return (
      <FullScreenFlowLayout maxWidth="sm">
        <Stack sx={{ height: '100%', justifyContent: 'center' }} spacing={3}>
          <BrandMark />
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
              <Box component="form" onSubmit={handleLogin}>
                <Stack spacing={3}>
                  <Box>
                    <Typography variant="h1" gutterBottom>
                      Admin
                    </Typography>
                    <Typography color="text.secondary">Ingresa tus credenciales para acceder al panel.</Typography>
                  </Box>
                  <TextField label="Username" value={username} onChange={(event) => setUsername(event.target.value)} required />
                  <TextField
                    label="Password"
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                  />
                  {error ? <Alert severity="error">{error}</Alert> : null}
                  <Button type="submit" size="large" variant="contained" startIcon={<LockOutlinedIcon />} disabled={loading}>
                    {loading ? 'Ingresando...' : 'Ingresar'}
                  </Button>
                </Stack>
              </Box>
            </CardContent>
          </Card>
        </Stack>
      </FullScreenFlowLayout>
    );
  }

  return (
    <Box sx={{ height: '100dvh', display: 'grid', gridTemplateColumns: { xs: '1fr', md: '260px 1fr' }, bgcolor: 'background.default' }}>
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': { position: 'static', width: 260, borderRight: '1px solid', borderColor: 'divider' },
        }}
      >
        <Stack sx={{ height: '100%', p: 2 }} spacing={2}>
          <BrandMark />
          <Divider />
          <Button
            startIcon={<DashboardOutlinedIcon />}
            variant={section === 'dashboard' ? 'contained' : 'text'}
            onClick={() => {
              setSection('dashboard');
              setError(null);
            }}
            sx={{ justifyContent: 'flex-start' }}
          >
            Dashboard
          </Button>
          <Button
            startIcon={<FlagOutlinedIcon />}
            variant={section === 'races' ? 'contained' : 'text'}
            onClick={() => {
              setSection('races');
              setWorkView('races-table');
              setError(null);
            }}
            sx={{ justifyContent: 'flex-start' }}
          >
            Carreras
          </Button>
          <Button
            startIcon={<PaymentsOutlinedIcon />}
            variant={section === 'payments' ? 'contained' : 'text'}
            onClick={() => {
              setSection('payments');
              setSelectedPaymentRace(null);
              setError(null);
              void loadPayments();
            }}
            sx={{ justifyContent: 'flex-start' }}
          >
            Pagos
          </Button>
          <Button
            startIcon={<CategoryOutlinedIcon />}
            variant={section === 'categories' ? 'contained' : 'text'}
            onClick={() => {
              setSection('categories');
              setWorkView('categories-table');
              setError(null);
            }}
            sx={{ justifyContent: 'flex-start' }}
          >
            Categorías
          </Button>
          <Box sx={{ flex: 1 }} />
          <Typography variant="body2" color="text.secondary">
            {sessionUsername}
          </Typography>
          <Button startIcon={<LogoutOutlinedIcon />} variant="outlined" onClick={handleLogout}>
            Logout
          </Button>
        </Stack>
      </Drawer>

      <Box component="main" sx={{ minWidth: 0, height: '100dvh', overflow: 'auto', p: { xs: 2, md: 3 } }}>
        <Stack spacing={3}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ display: { md: 'none' } }}>
            <Button
              variant={section === 'dashboard' ? 'contained' : 'outlined'}
              onClick={() => {
                setSection('dashboard');
                setError(null);
              }}
            >
              Dashboard
            </Button>
            <Button
              variant={section === 'races' ? 'contained' : 'outlined'}
              onClick={() => {
                setSection('races');
                setWorkView('races-table');
                setError(null);
              }}
            >
              Carreras
            </Button>
            <Button
              variant={section === 'payments' ? 'contained' : 'outlined'}
              onClick={() => {
                setSection('payments');
                setSelectedPaymentRace(null);
                setError(null);
                void loadPayments();
              }}
            >
              Pagos
            </Button>
            <Button
              variant={section === 'categories' ? 'contained' : 'outlined'}
              onClick={() => {
                setSection('categories');
                setWorkView('categories-table');
                setError(null);
              }}
            >
              Categorías
            </Button>
            <Button startIcon={<LogoutOutlinedIcon />} variant="outlined" onClick={handleLogout}>
              Logout
            </Button>
          </Stack>

          {error ? <Alert severity="error">{error}</Alert> : null}

          {section === 'dashboard' ? (
            <Stack spacing={3}>
              <Typography variant="h1">Dashboard</Typography>
              <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', maxWidth: 420 }}>
                <CardContent>
                  <Stack spacing={1}>
                    <Typography color="text.secondary">Corredores inscritos en la carrera activa</Typography>
                    <Typography variant="h1">{dashboard?.active_race_registered_bikers ?? 0}</Typography>
                    <Typography color="text.secondary">{dashboard?.active_race_name ?? 'Sin carrera activa'}</Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Stack>
          ) : null}

          {section === 'payments' ? (
            <Stack spacing={3}>
              <Typography variant="h1">Pagos</Typography>
              {selectedPaymentRace ? (
                <PaymentTable
                  race={selectedPaymentRace}
                  payments={selectedRacePayments}
                  loading={loading}
                  onBack={() => setSelectedPaymentRace(null)}
                  onOpenProof={handleOpenProofUrl}
                  onValidate={handleValidatePayment}
                />
              ) : (
                <PaymentRaceTable races={races} payments={payments} onViewPayments={setSelectedPaymentRace} />
              )}
            </Stack>
          ) : null}

          {section === 'categories' ? (
            <Stack spacing={3}>
              {workView === 'categories-table' ? (
                <>
                  <Typography variant="h1">Categorías</Typography>
                  <CategoryTable
                    categories={categories}
                    loading={loading}
                    onCreate={() => {
                      setCategoryForm(emptyCategoryForm);
                      setEditingCategoryId(null);
                      setWorkView('category-edit');
                    }}
                    onEdit={(category) => {
                      setCategoryForm(toCategoryForm(category));
                      setEditingCategoryId(category.id);
                      setWorkView('category-edit');
                    }}
                    onStatus={handleCategoryStatus}
                  />
                </>
              ) : null}
              {workView === 'category-edit' ? (
                <CategoryForm
                  form={categoryForm}
                  races={races}
                  editingCategoryId={editingCategoryId}
                  loading={loading}
                  onChange={setCategoryForm}
                  onBack={() => {
                    setCategoryForm(emptyCategoryForm);
                    setEditingCategoryId(null);
                    setWorkView('categories-table');
                  }}
                  onSubmit={handleCategorySubmit}
                />
              ) : null}
            </Stack>
          ) : null}

          {section === 'races' ? (
            <Stack spacing={3}>
              {workView === 'races-table' ? (
                <>
                  <Typography variant="h1">Carreras</Typography>
                  <RaceTable
                    races={paginatedRaces}
                    totalRaces={filteredRaces.length}
                    page={racePage}
                    search={raceSearch}
                    loading={loading}
                    onSearch={(value) => {
                      setRaceSearch(value);
                      setRacePage(0);
                    }}
                    onPageChange={setRacePage}
                    onCreate={() => {
                      setRaceForm(emptyRaceForm);
                      setEditingRaceId(null);
                      setWorkView('race-edit');
                    }}
                    onEdit={(race) => {
                      setRaceForm(toRaceForm(race));
                      setEditingRaceId(race.id);
                      setWorkView('race-edit');
                    }}
                    onDeactivate={handleDeactivateRace}
                    onViewBikers={(race) => void loadBikers(race, { page: 0, resetSearch: true })}
                    onViewMap={setMapPreviewRace}
                  />
                </>
              ) : null}
              {workView === 'race-edit' ? (
                <RaceForm
                  form={raceForm}
                  editingRaceId={editingRaceId}
                  loading={loading}
                  onChange={setRaceForm}
                  onBack={() => {
                    setRaceForm(emptyRaceForm);
                    setEditingRaceId(null);
                    setWorkView('races-table');
                  }}
                  onSubmit={handleRaceSubmit}
                />
              ) : null}
              {workView === 'bikers-table' && selectedRace ? (
                <BikerTable
                  race={selectedRace}
                  bikers={bikers}
                  totalBikers={bikerTotal}
                  page={bikerPage}
                  search={bikerSearch}
                  sortBy={bikerSortBy}
                  sortDirection={bikerSortDirection}
                  loading={loading}
                  onBack={() => {
                    setSelectedRace(null);
                    setBikers([]);
                    setBikerTotal(0);
                    setWorkView('races-table');
                  }}
                  onSearch={(value) => {
                    void loadBikers(selectedRace, { search: value, page: 0 });
                  }}
                  onPageChange={(page) => void loadBikers(selectedRace, { page })}
                  onSort={(sortBy) => {
                    const sortDirection = bikerSortBy === sortBy && bikerSortDirection === 'asc' ? 'desc' : 'asc';
                    void loadBikers(selectedRace, { page: 0, sortBy, sortDirection });
                  }}
                  onRequestStatus={setPendingStatusChange}
                  onExport={() => setBikerExportOpen(true)}
                  onEdit={(biker) => {
                    setEditingBiker(biker);
                    setBikerForm(toBikerForm(biker));
                    setWorkView('biker-edit');
                  }}
                  onOpenProof={handleOpenProof}
                />
              ) : null}
              {workView === 'biker-edit' && editingBiker && bikerForm ? (
                <BikerEditor
                  biker={editingBiker}
                  form={bikerForm}
                  loading={loading}
                  onChange={setBikerForm}
                  onBack={() => {
                    setEditingBiker(null);
                    setBikerForm(null);
                    setWorkView('bikers-table');
                  }}
                  onSubmit={handleBikerSubmit}
                />
              ) : null}
            </Stack>
          ) : null}
        </Stack>
      </Box>
      <Dialog open={pendingStatusChange !== null} onClose={() => setPendingStatusChange(null)}>
        <DialogTitle>Confirmar acción</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Desea {pendingStatusChange?.status === 'habilitado' ? 'habilitar' : 'deshabilitar'} el corredor?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPendingStatusChange(null)}>Cancelar</Button>
          <Button
            variant="contained"
            disabled={loading || pendingStatusChange === null}
            onClick={() => {
              if (pendingStatusChange) {
                void handleBikerStatus(pendingStatusChange.biker, pendingStatusChange.status);
              }
            }}
          >
            Confirmar
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog open={bikerExportOpen} onClose={() => setBikerExportOpen(false)}>
        <DialogTitle>Exportar Excel</DialogTitle>
        <DialogContent>
          <Stack spacing={1} sx={{ pt: 1 }}>
            {bikerExportOptions.map((option) => (
              <FormControlLabel
                key={option.field}
                control={
                  <Checkbox
                    checked={bikerExportFields.includes(option.field)}
                    onChange={(event) => {
                      setBikerExportFields((currentFields) =>
                        event.target.checked
                          ? [...currentFields, option.field]
                          : currentFields.filter((field) => field !== option.field),
                      );
                    }}
                  />
                }
                label={option.label}
              />
            ))}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBikerExportOpen(false)}>Cancelar</Button>
          <Button variant="contained" disabled={loading || bikerExportFields.length === 0} onClick={() => void handleExportBikers()}>
            Exportar
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog open={proofPreviewUrl !== null} maxWidth="md" fullWidth onClose={handleCloseProofPreview}>
        <DialogTitle>Comprobante</DialogTitle>
        <DialogContent>
          {proofPreviewUrl ? (
            <Box
              component="img"
              src={proofPreviewUrl}
              alt="Comprobante de pago"
              sx={{ width: '100%', maxHeight: '70dvh', objectFit: 'contain', display: 'block' }}
            />
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseProofPreview}>Cerrar</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={mapPreviewRace !== null} maxWidth="md" fullWidth onClose={() => setMapPreviewRace(null)}>
        <DialogTitle>
          <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="h3" sx={{ flex: 1 }}>
              Mapa Strava
            </Typography>
            <Tooltip title="Cerrar">
              <IconButton aria-label="Cerrar mapa" onClick={() => setMapPreviewRace(null)}>
                <CloseOutlinedIcon />
              </IconButton>
            </Tooltip>
          </Stack>
        </DialogTitle>
        <DialogContent>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: 320,
              '& iframe': { maxWidth: '100%', border: 0 },
            }}
          >
            {mapPreviewRace?.strava_map_html ? (
              <StravaMapEmbed html={mapPreviewRace.strava_map_html} />
            ) : (
              <Typography color="text.secondary">Esta carrera no tiene mapa configurado.</Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ justifyContent: 'center' }}>
          <Button variant="contained" onClick={() => setMapPreviewRace(null)}>
            Cerrar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

function paymentStatusColor(status: string): 'success' | 'error' | 'default' {
  if (status === 'validated') {
    return 'success';
  }
  if (status === 'rejected') {
    return 'error';
  }
  return 'default';
}

function categoryStatusColor(status: 'active' | 'deactive'): 'success' | 'default' {
  return status === 'active' ? 'success' : 'default';
}

function StravaMapEmbed({ html }: { html: string }) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return undefined;
    }

    container.innerHTML = html;
    const scripts = Array.from(container.querySelectorAll('script'));
    scripts.forEach((script) => script.remove());

    scripts.forEach((script) => {
      const executableScript = document.createElement('script');
      Array.from(script.attributes).forEach((attribute) => {
        executableScript.setAttribute(attribute.name, attribute.value);
      });
      executableScript.async = true;
      executableScript.text = script.text;
      container.appendChild(executableScript);
    });

    return () => {
      container.innerHTML = '';
    };
  }, [html]);

  return (
    <Box
      ref={containerRef}
      sx={{
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        '& .strava-embed-placeholder': { width: '100%' },
        '& iframe': { maxWidth: '100%', border: 0 },
      }}
    />
  );
}

function CategoryTable({
  categories,
  loading,
  onCreate,
  onEdit,
  onStatus,
}: {
  categories: AdminCategory[];
  loading: boolean;
  onCreate: () => void;
  onEdit: (category: AdminCategory) => void;
  onStatus: (category: AdminCategory, status: 'active' | 'deactive') => void;
}) {
  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
      <CardContent>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }}>
          <Box sx={{ flex: 1 }} />
          <Button startIcon={<AddOutlinedIcon />} variant="contained" onClick={onCreate}>
            Crear Nueva Categoría
          </Button>
        </Stack>
      </CardContent>
      <Box sx={{ overflow: 'auto' }}>
        <Table size="small">
          <TableHead sx={{ '& .MuiTableCell-root': { fontWeight: 800 } }}>
            <TableRow>
              <TableCell>Nombre</TableCell>
              <TableCell>Tipo</TableCell>
              <TableCell>Sexo</TableCell>
              <TableCell>Edad desde</TableCell>
              <TableCell>Edad hasta</TableCell>
              <TableCell>Nacidos desde</TableCell>
              <TableCell>Nacidos hasta</TableCell>
              <TableCell>Carreras</TableCell>
              <TableCell>Estado</TableCell>
              <TableCell align="right">Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {categories.map((category) => (
              <TableRow key={category.id} hover sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                <TableCell>{category.name}</TableCell>
                <TableCell>{category.category_type}</TableCell>
                <TableCell>{category.sex}</TableCell>
                <TableCell>{category.age_from}</TableCell>
                <TableCell>{category.age_to ?? '-'}</TableCell>
                <TableCell>{category.born_from}</TableCell>
                <TableCell>{category.born_to}</TableCell>
                <TableCell>{category.race_names.length > 0 ? category.race_names.join(', ') : '-'}</TableCell>
                <TableCell>
                  <Chip
                    size="small"
                    color={categoryStatusColor(category.status)}
                    label={category.status === 'active' ? 'Habilitada' : 'Deshabilitada'}
                  />
                </TableCell>
                <TableCell align="right">
                  <Tooltip title="Editar">
                    <IconButton aria-label="Editar categoría" onClick={() => onEdit(category)}>
                      <EditOutlinedIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Habilitar">
                    <span>
                      <IconButton
                        aria-label="Habilitar categoría"
                        color="success"
                        disabled={loading || category.status === 'active'}
                        onClick={() => onStatus(category, 'active')}
                      >
                        <CheckCircleOutlineIcon />
                      </IconButton>
                    </span>
                  </Tooltip>
                  <Tooltip title="Deshabilitar">
                    <span>
                      <IconButton
                        aria-label="Deshabilitar categoría"
                        color="error"
                        disabled={loading || category.status === 'deactive'}
                        onClick={() => onStatus(category, 'deactive')}
                      >
                        <CancelOutlinedIcon />
                      </IconButton>
                    </span>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
            {categories.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10}>
                  <Typography color="text.secondary">No se encontraron categorías.</Typography>
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </Box>
    </Card>
  );
}

function CategoryForm({
  form,
  races,
  editingCategoryId,
  loading,
  onChange,
  onBack,
  onSubmit,
}: {
  form: AdminCategoryPayload;
  races: AdminRace[];
  editingCategoryId: string | null;
  loading: boolean;
  onChange: (form: AdminCategoryPayload) => void;
  onBack: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  const currentYear = new Date().getFullYear();
  const birthYearOptions = Array.from({ length: currentYear - 1900 + 1 }, (_item, index) => currentYear - index);
  const ageToOptions = Array.from({ length: 101 }, (_item, index) => index);

  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
      <CardContent>
        <Box component="form" onSubmit={onSubmit}>
          <Stack spacing={2}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ sm: 'center' }}>
              <Button startIcon={<ArrowBackOutlinedIcon />} variant="outlined" onClick={onBack}>
                Atrás
              </Button>
              <Typography variant="h2">{editingCategoryId ? 'Actualizar categoría' : 'Crear categoría'}</Typography>
            </Stack>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr 1fr' }, gap: 2 }}>
              <TextField label="Nombre" value={form.name} onChange={(event) => onChange({ ...form, name: event.target.value })} required />
              <TextField
                select
                label="Tipo"
                value={form.category_type}
                onChange={(event) => onChange({ ...form, category_type: event.target.value as CategoryType })}
              >
                <MenuItem value="Cicloturista">Cicloturista</MenuItem>
                <MenuItem value="Aficionado">Aficionado</MenuItem>
                <MenuItem value="Federado">Federado</MenuItem>
              </TextField>
              <TextField
                select
                label="Sexo"
                value={form.sex}
                onChange={(event) => onChange({ ...form, sex: event.target.value as CategorySex })}
              >
                <MenuItem value="varones">Varones</MenuItem>
                <MenuItem value="damas">Damas</MenuItem>
              </TextField>
              <TextField
                label="Edad desde"
                type="number"
                value={form.age_from}
                onChange={(event) => onChange({ ...form, age_from: Number(event.target.value) })}
                required
              />
              <TextField
                select
                label="Edad hasta"
                value={form.age_to ?? '-'}
                onChange={(event) => onChange({ ...form, age_to: event.target.value === '-' ? null : Number(event.target.value) })}
              >
                <MenuItem value="-">-</MenuItem>
                {ageToOptions.map((age) => (
                  <MenuItem key={age} value={age}>
                    {age}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Nacidos desde"
                value={form.born_from}
                onChange={(event) => onChange({ ...form, born_from: Number(event.target.value) })}
              >
                {birthYearOptions.map((year) => (
                  <MenuItem key={year} value={year}>
                    {year}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Carreras"
                value={form.race_ids}
                onChange={(event) => {
                  const value = event.target.value;
                  onChange({ ...form, race_ids: typeof value === 'string' ? value.split(',') : value });
                }}
                SelectProps={{
                  multiple: true,
                  renderValue: (selected) => {
                    const selectedIds = selected as string[];
                    const selectedNames = races.filter((race) => selectedIds.includes(race.id)).map((race) => race.name);
                    return selectedNames.length > 0 ? selectedNames.join(', ') : 'Sin carreras';
                  },
                }}
              >
                {races.map((race) => (
                  <MenuItem key={race.id} value={race.id}>
                    <Checkbox checked={form.race_ids.includes(race.id)} />
                    {race.name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Nacidos hasta"
                value={form.born_to}
                onChange={(event) => onChange({ ...form, born_to: Number(event.target.value) })}
              >
                {birthYearOptions.map((year) => (
                  <MenuItem key={year} value={year}>
                    {year}
                  </MenuItem>
                ))}
              </TextField>
            </Box>
            <Stack direction="row" spacing={1}>
              <Button type="submit" variant="contained" startIcon={<AddOutlinedIcon />} disabled={loading}>
                {editingCategoryId ? 'Guardar cambios' : 'Crear categoría'}
              </Button>
            </Stack>
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
}

function paymentCountsAsCollected(payment: AdminPayment): boolean {
  return payment.status === 'validated' && payment.biker_count > 0 && payment.enabled_biker_count === payment.biker_count;
}

function collectedAmountForPayments(payments: AdminPayment[]): number {
  return payments.reduce((total, payment) => {
    if (!paymentCountsAsCollected(payment)) {
      return total;
    }
    return total + Number(payment.validated_amount ?? payment.expected_amount ?? 0);
  }, 0);
}

function PaymentRaceTable({
  races,
  payments,
  onViewPayments,
}: {
  races: AdminRace[];
  payments: AdminPayment[];
  onViewPayments: (race: AdminRace) => void;
}) {
  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
      <Box sx={{ overflow: 'auto' }}>
        <Table size="small">
          <TableHead sx={{ '& .MuiTableCell-root': { fontWeight: 800 } }}>
            <TableRow>
              <TableCell>Carrera</TableCell>
              <TableCell>Gestión</TableCell>
              <TableCell>Pagos</TableCell>
              <TableCell>Total recaudado</TableCell>
              <TableCell align="right">Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {races.map((race) => {
              const racePayments = payments.filter((payment) => payment.race_id === race.id);
              return (
                <TableRow key={race.id} hover sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                  <TableCell>
                    <Typography fontWeight={700}>{race.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {race.location_name}
                    </Typography>
                  </TableCell>
                  <TableCell>{race.year}</TableCell>
                  <TableCell>{racePayments.length}</TableCell>
                  <TableCell>{formatMoney(collectedAmountForPayments(racePayments), race.currency)}</TableCell>
                  <TableCell align="right">
                    <Tooltip title="Ver pagos">
                      <IconButton aria-label="Ver pagos" onClick={() => onViewPayments(race)}>
                        <PaymentsOutlinedIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              );
            })}
            {races.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5}>
                  <Typography color="text.secondary">No se encontraron carreras.</Typography>
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </Box>
    </Card>
  );
}

function PaymentTable({
  race,
  payments,
  loading,
  onBack,
  onOpenProof,
  onValidate,
}: {
  race: AdminRace;
  payments: AdminPayment[];
  loading: boolean;
  onBack: () => void;
  onOpenProof: (paymentProofUrl: string | null) => void;
  onValidate: (payment: AdminPayment) => void;
}) {
  const totalCollected = collectedAmountForPayments(payments);
  const [paymentPage, setPaymentPage] = useState(0);
  const paginatedPayments = useMemo(
    () => payments.slice(paymentPage * 50, paymentPage * 50 + 50),
    [paymentPage, payments],
  );

  useEffect(() => {
    setPaymentPage(0);
  }, [payments.length, race.id]);

  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
      <CardContent>
        <Stack spacing={2}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ sm: 'center' }}>
            <Button startIcon={<ArrowBackOutlinedIcon />} variant="outlined" onClick={onBack}>
              Atrás
            </Button>
            <Box>
              <Typography variant="h2">{race.name}</Typography>
              <Typography color="text.secondary">
                {race.location_name} · {race.year}
              </Typography>
            </Box>
          </Stack>
          <Box>
            <Typography color="text.secondary">Total recaudado</Typography>
            <Typography variant="h2">{formatMoney(totalCollected, race.currency)}</Typography>
          </Box>
        </Stack>
      </CardContent>
      <Box sx={{ overflow: 'auto' }}>
        <Table size="small">
          <TableHead sx={{ '& .MuiTableCell-root': { fontWeight: 800 } }}>
            <TableRow>
              <TableCell>Fecha y hora</TableCell>
              <TableCell>ID transacción</TableCell>
              <TableCell>Monto detectado</TableCell>
              <TableCell>Monto validado</TableCell>
              <TableCell>Comprobante</TableCell>
              <TableCell>Estado</TableCell>
              <TableCell>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedPayments.map((payment) => (
              <TableRow key={payment.id} hover sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                <TableCell>
                  {new Date(payment.created_at).toLocaleString()}
                  <Typography variant="caption" color="text.secondary" display="block">
                    {payment.payment_kind} · Corredores: {payment.enabled_biker_count}/{payment.biker_count}
                  </Typography>
                </TableCell>
                <TableCell>{payment.transaction_id ?? '-'}</TableCell>
                <TableCell>{formatMoney(payment.extracted_amount, payment.currency)}</TableCell>
                <TableCell>{formatMoney(payment.validated_amount, payment.currency)}</TableCell>
                <TableCell>
                  <Tooltip title="Ver">
                    <IconButton size="small" aria-label="Ver comprobante" onClick={() => onOpenProof(payment.payment_proof_url)}>
                      <VisibilityOutlinedIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </TableCell>
                <TableCell>
                  <Chip size="small" color={paymentStatusColor(payment.status)} label={payment.status} />
                </TableCell>
                <TableCell>
                  <Tooltip title="Validar pago">
                    <span>
                      <IconButton
                        color="success"
                        aria-label="Validar pago"
                        disabled={loading || !payment.can_validate}
                        onClick={() => onValidate(payment)}
                      >
                        <CheckCircleOutlineIcon />
                      </IconButton>
                    </span>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
            {paginatedPayments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7}>
                  <Typography color="text.secondary">No se encontraron pagos.</Typography>
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </Box>
      <TablePagination
        component="div"
        count={payments.length}
        page={paymentPage}
        rowsPerPage={50}
        rowsPerPageOptions={[50]}
        onPageChange={(_event, nextPage) => setPaymentPage(nextPage)}
      />
    </Card>
  );
}

function RaceForm({
  form,
  editingRaceId,
  loading,
  onChange,
  onBack,
  onSubmit,
}: {
  form: AdminRacePayload;
  editingRaceId: string | null;
  loading: boolean;
  onChange: (form: AdminRacePayload) => void;
  onBack: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
      <CardContent>
        <Box component="form" onSubmit={onSubmit}>
          <Stack spacing={2}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ sm: 'center' }}>
              <Button startIcon={<ArrowBackOutlinedIcon />} variant="outlined" onClick={onBack}>
                Atrás
              </Button>
              <Typography variant="h2">{editingRaceId ? 'Actualizar carrera' : 'Crear carrera'}</Typography>
            </Stack>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr 1fr' }, gap: 2 }}>
              <TextField label="Nombre" value={form.name} onChange={(event) => onChange({ ...form, name: event.target.value })} required />
              <TextField
                label="Gestión"
                type="number"
                value={form.year}
                onChange={(event) => onChange({ ...form, year: Number(event.target.value) })}
                required
              />
              <TextField
                select
                label="Estado"
                value={form.status}
                onChange={(event) => onChange({ ...form, status: event.target.value as RaceStatus })}
              >
                <MenuItem value="active">Activa</MenuItem>
                <MenuItem value="deactive">Inactiva</MenuItem>
              </TextField>
              <TextField
                label="Ubicación"
                value={form.location_name}
                onChange={(event) => onChange({ ...form, location_name: event.target.value })}
                required
              />
              <TextField
                label="Fecha"
                type="date"
                value={form.date_of_race ?? ''}
                onChange={(event) => onChange({ ...form, date_of_race: event.target.value || null })}
                InputLabelProps={{ shrink: true }}
              />
              <TextField
                label="Costo"
                type="number"
                value={form.cost}
                onChange={(event) => onChange({ ...form, cost: Number(event.target.value) })}
                required
              />
              <TextField
                select
                label="Moneda"
                value={form.currency}
                onChange={(event) => onChange({ ...form, currency: event.target.value as 'BOB' | 'USD' })}
              >
                <MenuItem value="BOB">BOB</MenuItem>
                <MenuItem value="USD">USD</MenuItem>
              </TextField>
              <TextField
                label="Detalle ubicación"
                value={form.location ?? ''}
                onChange={(event) => onChange({ ...form, location: event.target.value })}
                sx={{ gridColumn: { md: 'span 2' } }}
              />
              <TextField
                label="HTML mapa Strava"
                value={form.strava_map_html ?? ''}
                onChange={(event) => onChange({ ...form, strava_map_html: event.target.value })}
                multiline
                minRows={5}
                sx={{ gridColumn: { md: 'span 3' } }}
              />
            </Box>
            <Stack direction="row" spacing={1}>
              <Button type="submit" variant="contained" startIcon={<AddOutlinedIcon />} disabled={loading}>
                {editingRaceId ? 'Guardar cambios' : 'Crear carrera'}
              </Button>
            </Stack>
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
}

function RaceTable({
  races,
  totalRaces,
  page,
  search,
  loading,
  onSearch,
  onPageChange,
  onCreate,
  onEdit,
  onDeactivate,
  onViewBikers,
  onViewMap,
}: {
  races: AdminRace[];
  totalRaces: number;
  page: number;
  search: string;
  loading: boolean;
  onSearch: (value: string) => void;
  onPageChange: (page: number) => void;
  onCreate: () => void;
  onEdit: (race: AdminRace) => void;
  onDeactivate: (race: AdminRace) => void;
  onViewBikers: (race: AdminRace) => void;
  onViewMap: (race: AdminRace) => void;
}) {
  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
      <CardContent>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }}>
          <TextField
            label="Buscar carrera"
            value={search}
            onChange={(event) => onSearch(event.target.value)}
            sx={{ minWidth: { md: 360 } }}
          />
          <Box sx={{ flex: 1 }} />
          <Button startIcon={<AddOutlinedIcon />} variant="contained" onClick={onCreate}>
            Crear carrera
          </Button>
        </Stack>
      </CardContent>
      <Box sx={{ overflow: 'auto' }}>
        <Table size="small">
          <TableHead sx={{ '& .MuiTableCell-root': { fontWeight: 800 } }}>
            <TableRow>
              <TableCell>Carrera</TableCell>
              <TableCell>Gestión</TableCell>
              <TableCell>Estado</TableCell>
              <TableCell>Inscritos</TableCell>
              <TableCell>Mapa</TableCell>
              <TableCell align="right">Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {races.map((race) => (
              <TableRow key={race.id} hover sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                <TableCell>
                  <Typography fontWeight={700}>{race.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {race.location_name}
                  </Typography>
                </TableCell>
                <TableCell>{race.year}</TableCell>
                <TableCell>
                  <Chip size="small" color={race.status === 'active' ? 'success' : 'default'} label={race.status === 'active' ? 'Activa' : 'Inactiva'} />
                </TableCell>
                <TableCell>{race.registered_bikers}</TableCell>
                <TableCell>
                  <Button
                    size="small"
                    disabled={!race.strava_map_html}
                    onClick={() => onViewMap(race)}
                  >
                    Mostrar Mapa
                  </Button>
                </TableCell>
                <TableCell align="right">
                  <Tooltip title="Corredores">
                    <IconButton aria-label="Ver corredores" onClick={() => onViewBikers(race)}>
                      <DirectionsBikeOutlinedIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Editar">
                    <IconButton aria-label="Editar carrera" onClick={() => onEdit(race)}>
                      <EditOutlinedIcon />
                    </IconButton>
                  </Tooltip>
                  <Button size="small" disabled={loading || race.status !== 'active'} onClick={() => onDeactivate(race)}>
                    Desactivar
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            {races.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6}>
                  <Typography color="text.secondary">No se encontraron carreras.</Typography>
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </Box>
      <TablePagination
        component="div"
        count={totalRaces}
        page={page}
        rowsPerPage={10}
        rowsPerPageOptions={[10]}
        onPageChange={(_event, nextPage) => onPageChange(nextPage)}
      />
    </Card>
  );
}

function BikerTable({
  race,
  bikers,
  totalBikers,
  page,
  search,
  sortBy,
  sortDirection,
  loading,
  onBack,
  onSearch,
  onPageChange,
  onSort,
  onRequestStatus,
  onExport,
  onEdit,
  onOpenProof,
}: {
  race: AdminRace;
  bikers: AdminBiker[];
  totalBikers: number;
  page: number;
  search: string;
  sortBy: BikerSortBy;
  sortDirection: SortDirection;
  loading: boolean;
  onBack: () => void;
  onSearch: (value: string) => void;
  onPageChange: (page: number) => void;
  onSort: (sortBy: BikerSortBy) => void;
  onRequestStatus: (change: { biker: AdminBiker; status: BikerStatus }) => void;
  onExport: () => void;
  onEdit: (biker: AdminBiker) => void;
  onOpenProof: (biker: AdminBiker) => void;
}) {
  const sortHeader = (field: BikerSortBy, label: string) => (
    <TableSortLabel active={sortBy === field} direction={sortBy === field ? sortDirection : 'asc'} onClick={() => onSort(field)}>
      {label}
    </TableSortLabel>
  );

  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
      <CardContent>
        <Stack spacing={2}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ sm: 'center' }}>
            <Button startIcon={<ArrowBackOutlinedIcon />} variant="outlined" onClick={onBack}>
              Atrás
            </Button>
            <Typography variant="h2">Corredores: {race.name}</Typography>
            <Box sx={{ flex: 1 }} />
            <Button startIcon={<FileDownloadOutlinedIcon />} variant="outlined" onClick={onExport}>
              Exportar Excel
            </Button>
          </Stack>
          <TextField label="Buscar competidor" value={search} onChange={(event) => onSearch(event.target.value)} sx={{ maxWidth: 420 }} />
        </Stack>
      </CardContent>
      <Box sx={{ overflow: 'auto' }}>
        <Table size="small">
          <TableHead sx={{ '& .MuiTableCell-root': { fontWeight: 800 } }}>
            <TableRow>
              <TableCell>{sortHeader('full_name', 'Nombres')}</TableCell>
              <TableCell>{sortHeader('gender', 'Sexo')}</TableCell>
              <TableCell>{sortHeader('age', 'Edad')}</TableCell>
              <TableCell>{sortHeader('bike_team_name', 'Equipo')}</TableCell>
              <TableCell>{sortHeader('detected_category', 'Categoría')}</TableCell>
              <TableCell>{sortHeader('created_at', 'Fecha inscripción')}</TableCell>
              <TableCell>Comprobante</TableCell>
              <TableCell>{sortHeader('status', 'Estado')}</TableCell>
              <TableCell align="right">Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {bikers.map((biker) => (
              <TableRow key={biker.id} hover sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                <TableCell>{toUpperText(biker.full_name)}</TableCell>
                <TableCell>
                  <Tooltip title={genderTooltip(biker.gender)}>
                    <PersonOutlineOutlinedIcon
                      aria-label={genderTooltip(biker.gender)}
                      sx={{ color: genderIconColor(biker.gender), display: 'block' }}
                    />
                  </Tooltip>
                </TableCell>
                <TableCell>{biker.age}</TableCell>
                <TableCell>{biker.bike_team_name}</TableCell>
                <TableCell>{toUpperText(biker.detected_category)}</TableCell>
                <TableCell>{new Date(biker.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <Tooltip title="Ver">
                    <span>
                      <IconButton
                        size="small"
                        aria-label="Ver comprobante"
                        disabled={!biker.payment_proof_url}
                        onClick={() => onOpenProof(biker)}
                      >
                        <VisibilityOutlinedIcon fontSize="small" />
                      </IconButton>
                    </span>
                  </Tooltip>
                </TableCell>
                <TableCell>
                  <Chip
                    size="small"
                    color={bikerStatusChipColor(biker.status)}
                    icon={statusIcon(biker.status)}
                    label={biker.status}
                  />
                </TableCell>
                <TableCell align="right">
                  <Tooltip title="Editar">
                    <IconButton aria-label="Editar corredor" onClick={() => onEdit(biker)}>
                      <EditOutlinedIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Habilitar">
                    <span>
                      <IconButton
                        aria-label="Habilitar corredor"
                        color="success"
                        disabled={loading || biker.status === 'habilitado'}
                        onClick={() => onRequestStatus({ biker, status: 'habilitado' })}
                      >
                        <CheckCircleOutlineIcon />
                      </IconButton>
                    </span>
                  </Tooltip>
                  <Tooltip title="Deshabilitar">
                    <span>
                      <IconButton
                        aria-label="Deshabilitar corredor"
                        color="error"
                        disabled={loading || biker.status === 'deshabilitado'}
                        onClick={() => onRequestStatus({ biker, status: 'deshabilitado' })}
                      >
                        <CancelOutlinedIcon />
                      </IconButton>
                    </span>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
            {bikers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9}>
                  <Typography color="text.secondary">No se encontraron competidores.</Typography>
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </Box>
      <TablePagination
        component="div"
        count={totalBikers}
        page={page}
        rowsPerPage={50}
        rowsPerPageOptions={[50]}
        onPageChange={(_event, nextPage) => onPageChange(nextPage)}
      />
    </Card>
  );
}

function BikerEditor({
  biker,
  form,
  loading,
  onChange,
  onBack,
  onSubmit,
}: {
  biker: AdminBiker | null;
  form: AdminBikerPayload | null;
  loading: boolean;
  onChange: (form: AdminBikerPayload | null) => void;
  onBack: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  if (!biker || !form) {
    return null;
  }

  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
      <CardContent>
        <Box component="form" onSubmit={onSubmit}>
          <Stack spacing={2}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ sm: 'center' }}>
              <Button startIcon={<ArrowBackOutlinedIcon />} variant="outlined" onClick={onBack}>
                Atrás
              </Button>
              <Typography variant="h2">Editar corredor: {biker.full_name}</Typography>
            </Stack>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2, pt: 1 }}>
            <TextField label="Nombres" value={form.full_name} onChange={(event) => onChange({ ...form, full_name: event.target.value })} required />
            <TextField label="Email" value={form.email} onChange={(event) => onChange({ ...form, email: event.target.value })} required />
            <TextField label="DNI" value={form.dni} onChange={(event) => onChange({ ...form, dni: event.target.value })} required />
            <TextField
              label="Extensión"
              value={form.dni_extension}
              onChange={(event) => onChange({ ...form, dni_extension: event.target.value })}
              required
            />
            <TextField
              label="Fecha nacimiento"
              type="date"
              value={form.birth_date}
              onChange={(event) => onChange({ ...form, birth_date: event.target.value })}
              InputLabelProps={{ shrink: true }}
              required
            />
            <TextField
              select
              label="Sexo"
              value={form.gender}
              onChange={(event) => onChange({ ...form, gender: event.target.value as BikerGender })}
            >
              <MenuItem value="hombre">Hombre</MenuItem>
              <MenuItem value="mujer">Mujer</MenuItem>
            </TextField>
            <TextField label="Equipo" value={form.bike_team_name} onChange={(event) => onChange({ ...form, bike_team_name: event.target.value })} required />
            <TextField
              label="Categoría solicitada"
              value={form.requested_category}
              onChange={(event) => onChange({ ...form, requested_category: event.target.value })}
              required
            />
            <TextField
              label="Categoría detectada"
              value={form.detected_category}
              onChange={(event) => onChange({ ...form, detected_category: event.target.value })}
              required
            />
            <TextField
              label="Estado pago"
              value={form.payment_status}
              onChange={(event) => onChange({ ...form, payment_status: event.target.value })}
              required
            />
            <TextField
              label="Referencia pago"
              value={form.payment_reference}
              onChange={(event) => onChange({ ...form, payment_reference: event.target.value })}
              required
            />
            <TextField
              select
              label="Estado corredor"
              value={form.status}
              onChange={(event) => onChange({ ...form, status: event.target.value as BikerStatus })}
            >
              <MenuItem value="habilitado">Habilitado</MenuItem>
              <MenuItem value="deshabilitado">Deshabilitado</MenuItem>
              <MenuItem value="pendiente">Pendiente</MenuItem>
            </TextField>
          </Box>
            <Stack direction="row" spacing={1}>
              <Button type="submit" variant="contained" disabled={loading}>
                Guardar
              </Button>
            </Stack>
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
}
