export interface FirstRaceRegistrationReview {
  reviewToken: string;
  raceId: string;
  raceName: string;
  age: number;
  dni: string;
  dniExtension: string;
  fullName: string;
  email: string;
  birthDate: string;
  requestedCategory: string;
  detectedCategory: string;
  bikeTeamName: string;
  paymentId: string;
  paymentStatus: string;
  paymentReference: string;
  paymentMessage: string;
  paymentExpectedAmount: string;
  paymentExtractedAmount?: string | null;
  paymentCurrency: string;
  paymentTransactionId?: string | null;
  paymentDate?: string | null;
  paymentBankName?: string | null;
  categoryMessage: string;
  rulesSource: string;
}

export interface RegistrationConfirmResult {
  id: string;
  raceId: string;
  raceName: string;
  message: string;
}
