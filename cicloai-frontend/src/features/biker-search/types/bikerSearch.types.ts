export interface BikerSearchResult {
  id: string;
  fullName: string;
  dni: string;
  birthDate: string;
  cellphone?: string | null;
  teamName?: string | null;
  category: string;
  lastRegisteredRace?: {
    id: string;
    name: string;
  } | null;
}

export interface BikerLookupActionRequest {
  bikeRaceId?: string;
  searchedName: string;
  newTeamName: string;
  confirmAction: boolean;
}

export interface BikerLookupActionResult {
  status: 'completed';
  message: string;
  biker: {
    id: string;
    fullName: string;
    teamName: string;
  };
  nextAction: 'CONTINUE_TO_PAYMENT_LATER';
}
