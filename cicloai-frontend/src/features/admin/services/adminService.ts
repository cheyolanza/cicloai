import { appConfig } from '@/config/env';
import { httpClient } from '@/services/http/httpClient';
import { adminTokenStorage } from '@/features/admin/services/adminTokenStorage';

export type RaceStatus = 'active' | 'deactive';
export type CategoryStatus = 'active' | 'deactive';
export type CategorySex = 'varones' | 'damas';
export type CategoryType = 'Cicloturista' | 'Aficionado' | 'Federado';
export type BikerStatus = 'habilitado' | 'deshabilitado' | 'pendiente';
export type BikerGender = 'hombre' | 'mujer';
export type BikerSortBy = 'full_name' | 'gender' | 'age' | 'bike_team_name' | 'detected_category' | 'created_at' | 'status';
export type SortDirection = 'asc' | 'desc';

export interface AdminDashboard {
  active_race_id: string | null;
  active_race_name: string | null;
  active_race_registered_bikers: number;
}

export interface AdminRacePayload {
  name: string;
  location_name: string;
  location: string | null;
  strava_map_html: string | null;
  year: number;
  date_of_race: string | null;
  status: RaceStatus;
  cost: number;
  currency: 'BOB' | 'USD';
}

export interface AdminRace extends AdminRacePayload {
  id: string;
  registered_bikers: number;
  created_at: string;
  updated_at: string;
}

export interface AdminCategoryPayload {
  name: string;
  category_type: CategoryType;
  sex: CategorySex;
  age_from: number;
  age_to: number | null;
  born_from: number;
  born_to: number;
  race_ids: string[];
}

export interface AdminCategory extends AdminCategoryPayload {
  id: string;
  race_names: string[];
  status: CategoryStatus;
  created_at: string;
  updated_at: string;
}

export interface AdminBikerPayload {
  full_name: string;
  email: string;
  dni: string;
  dni_extension: string;
  birth_date: string;
  gender: BikerGender;
  requested_category: string;
  detected_category: string;
  bike_team_name: string;
  payment_status: string;
  payment_reference: string;
  status: BikerStatus;
}

export interface AdminBiker extends AdminBikerPayload {
  id: string;
  race_id: string;
  age: number;
  created_at: string;
  updated_at: string;
  payment_id: string | null;
  payment_proof_url: string | null;
}

export interface AdminBikerListResponse {
  items: AdminBiker[];
  total: number;
  page: number;
  page_size: number;
}

export interface AdminBikerListParams {
  page: number;
  pageSize: number;
  search: string;
  sortBy: BikerSortBy;
  sortDirection: SortDirection;
}

export type BikerExportField = 'full_name' | 'gender' | 'detected_category' | 'age' | 'bike_team_name';

export interface AdminPaymentBiker {
  id: string;
  full_name: string;
  status: BikerStatus;
}

export interface AdminPayment {
  id: string;
  race_id: string;
  race_name: string;
  race_location_name: string;
  race_year: number;
  created_at: string;
  transaction_id: string | null;
  extracted_amount: string | null;
  validated_amount: string | null;
  expected_amount: string;
  currency: 'BOB' | 'USD';
  total_collected: string;
  payment_proof_url: string;
  status: string;
  payment_kind: 'individual' | 'grupal';
  biker_count: number;
  enabled_biker_count: number;
  can_validate: boolean;
  bikers: AdminPaymentBiker[];
}

function getAdminToken(): string {
  const token = adminTokenStorage.get();
  if (!token) {
    throw new Error('Sesión de administrador requerida.');
  }
  return token;
}

export const adminService = {
  dashboard(): Promise<AdminDashboard> {
    return httpClient<AdminDashboard>('/admin/dashboard', { authToken: getAdminToken() });
  },
  listRaces(): Promise<AdminRace[]> {
    return httpClient<AdminRace[]>('/admin/races', { authToken: getAdminToken() });
  },
  createRace(payload: AdminRacePayload): Promise<AdminRace> {
    return httpClient<AdminRace>('/admin/races', {
      method: 'POST',
      authToken: getAdminToken(),
      body: JSON.stringify(payload),
    });
  },
  updateRace(raceId: string, payload: AdminRacePayload): Promise<AdminRace> {
    return httpClient<AdminRace>(`/admin/races/${raceId}`, {
      method: 'PUT',
      authToken: getAdminToken(),
      body: JSON.stringify(payload),
    });
  },
  deactivateRace(raceId: string): Promise<AdminRace> {
    return httpClient<AdminRace>(`/admin/races/${raceId}/deactivate`, {
      method: 'POST',
      authToken: getAdminToken(),
    });
  },
  listCategories(): Promise<AdminCategory[]> {
    return httpClient<AdminCategory[]>('/admin/categories', { authToken: getAdminToken() });
  },
  createCategory(payload: AdminCategoryPayload): Promise<AdminCategory> {
    return httpClient<AdminCategory>('/admin/categories', {
      method: 'POST',
      authToken: getAdminToken(),
      body: JSON.stringify(payload),
    });
  },
  updateCategory(categoryId: string, payload: AdminCategoryPayload): Promise<AdminCategory> {
    return httpClient<AdminCategory>(`/admin/categories/${categoryId}`, {
      method: 'PUT',
      authToken: getAdminToken(),
      body: JSON.stringify(payload),
    });
  },
  updateCategoryStatus(categoryId: string, status: CategoryStatus): Promise<AdminCategory> {
    return httpClient<AdminCategory>(`/admin/categories/${categoryId}/status`, {
      method: 'PATCH',
      authToken: getAdminToken(),
      body: JSON.stringify({ status }),
    });
  },
  listBikers(raceId: string, params: AdminBikerListParams): Promise<AdminBikerListResponse> {
    const query = new URLSearchParams({
      page: String(params.page),
      page_size: String(params.pageSize),
      search: params.search,
      sort_by: params.sortBy,
      sort_direction: params.sortDirection,
    });
    return httpClient<AdminBikerListResponse>(`/admin/races/${raceId}/bikers?${query.toString()}`, {
      authToken: getAdminToken(),
    });
  },
  updateBiker(bikerId: string, payload: AdminBikerPayload): Promise<AdminBiker> {
    return httpClient<AdminBiker>(`/admin/bikers/${bikerId}`, {
      method: 'PUT',
      authToken: getAdminToken(),
      body: JSON.stringify(payload),
    });
  },
  updateBikerStatus(bikerId: string, status: BikerStatus): Promise<AdminBiker> {
    return httpClient<AdminBiker>(`/admin/bikers/${bikerId}/status`, {
      method: 'PATCH',
      authToken: getAdminToken(),
      body: JSON.stringify({ status }),
    });
  },
  async exportBikersExcel(raceId: string, fields: BikerExportField[]): Promise<void> {
    const query = new URLSearchParams();
    fields.forEach((field) => query.append('fields', field));
    const response = await fetch(`${appConfig.apiBaseUrl}/admin/races/${raceId}/bikers/export?${query.toString()}`, {
      headers: {
        Authorization: `Bearer ${getAdminToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('No se pudo exportar corredores.');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'corredores-cicloai.xls';
    anchor.click();
    window.URL.revokeObjectURL(url);
  },
  listPayments(): Promise<AdminPayment[]> {
    return httpClient<AdminPayment[]>('/admin/payments', { authToken: getAdminToken() });
  },
  validatePayment(paymentId: string): Promise<AdminPayment> {
    return httpClient<AdminPayment>(`/admin/payments/${paymentId}/validate`, {
      method: 'POST',
      authToken: getAdminToken(),
    });
  },
  async loadPaymentProof(paymentProofUrl: string): Promise<string> {
    const response = await fetch(`${appConfig.apiBaseUrl}${paymentProofUrl.replace('/api/v1', '')}`, {
      headers: {
        Authorization: `Bearer ${getAdminToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('No se pudo abrir el comprobante.');
    }

    const blob = await response.blob();
    return window.URL.createObjectURL(blob);
  },
};
