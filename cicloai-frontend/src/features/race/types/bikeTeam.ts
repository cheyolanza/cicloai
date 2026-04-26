export interface BikeTeam {
  id: string;
  name: string;
  active: boolean;
  managerName?: string | null;
  contactPhone?: string | null;
  facebookPage?: string | null;
  pictureUrl?: string | null;
}
