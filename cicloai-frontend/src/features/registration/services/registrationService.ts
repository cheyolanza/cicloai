import { appConfig } from '@/config/env';
import type { NewUserRegistration } from '@/features/agent/types/registration';
import { tokenService } from '@/features/access/services/tokenService';
import type {
  FirstRaceRegistrationReview,
  RegistrationConfirmResult,
} from '@/features/registration/types/registrationReview';

interface FirstRaceRegistrationReviewApiResponse {
  review_token: string;
  race_id: string;
  race_name: string;
  age: number;
  dni: string;
  dni_extension: string;
  full_name: string;
  email: string;
  birth_date: string;
  gender: string;
  requested_category: string;
  detected_category: string;
  bike_team_name: string;
  payment_id: string;
  payment_status: string;
  payment_reference: string;
  payment_message: string;
  payment_expected_amount: string;
  payment_extracted_amount?: string | null;
  payment_currency: string;
  payment_transaction_id?: string | null;
  payment_date?: string | null;
  payment_bank_name?: string | null;
  category_message: string;
  rules_source: string;
}

interface RegistrationConfirmApiResponse {
  id: string;
  race_id: string;
  race_name: string;
  message: string;
}

function requireAccessToken(): string {
  const token = tokenService.getToken();
  if (!token) {
    throw new Error('Operación no permitida. El usuario debe validarse.');
  }
  return token;
}

async function readError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string };
    return payload.detail ?? `HTTP ${response.status}: ${response.statusText}`;
  } catch {
    return `HTTP ${response.status}: ${response.statusText}`;
  }
}

function mapReview(response: FirstRaceRegistrationReviewApiResponse): FirstRaceRegistrationReview {
  return {
    reviewToken: response.review_token,
    raceId: response.race_id,
    raceName: response.race_name,
    age: response.age,
    dni: response.dni,
    dniExtension: response.dni_extension,
    fullName: response.full_name,
    email: response.email,
    birthDate: response.birth_date,
    requestedCategory: response.requested_category,
    detectedCategory: response.detected_category,
    bikeTeamName: response.bike_team_name,
    paymentId: response.payment_id,
    paymentStatus: response.payment_status,
    paymentReference: response.payment_reference,
    paymentMessage: response.payment_message,
    paymentExpectedAmount: response.payment_expected_amount,
    paymentExtractedAmount: response.payment_extracted_amount ?? null,
    paymentCurrency: response.payment_currency,
    paymentTransactionId: response.payment_transaction_id ?? null,
    paymentDate: response.payment_date ?? null,
    paymentBankName: response.payment_bank_name ?? null,
    categoryMessage: response.category_message,
    rulesSource: response.rules_source,
  };
}

/**
 * Backend boundary for registration review and final confirmation.
 * The first call sends form data plus the uploaded proof; the second call
 * confirms the signed review token so the database insert happens only after
 * explicit Human-in-the-Loop approval from the user.
 */
export const registrationService = {
  async reviewFirstRaceRegistration(
    registration: NewUserRegistration,
    paymentProof: File,
  ): Promise<FirstRaceRegistrationReview> {
    const form = new FormData();
    form.set('dni', registration.dni);
    form.set('dni_extension', registration.dniExtension);
    form.set('full_name', registration.fullName);
    form.set('email', registration.email);
    form.set('birth_date', registration.birthDate);
    form.set('gender', registration.gender);
    form.set('requested_category', registration.category);
    form.set('bike_team_name', registration.team);
    form.set('payment_proof', paymentProof);

    console.info('[CicloAI] POST /api/v1/registrations/first-race/review', {
      dni: registration.dni,
      dniExtension: registration.dniExtension,
      fullName: registration.fullName,
      email: registration.email,
      birthDate: registration.birthDate,
      gender: registration.gender,
      requestedCategory: registration.category,
      bikeTeamName: registration.team,
      paymentProof: {
        name: paymentProof.name,
        type: paymentProof.type,
        sizeBytes: paymentProof.size,
      },
    });

    const response = await fetch(`${appConfig.apiBaseUrl}/registrations/first-race/review`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${requireAccessToken()}`,
      },
      body: form,
    });

    if (!response.ok) {
      throw new Error(await readError(response));
    }

    return mapReview((await response.json()) as FirstRaceRegistrationReviewApiResponse);
  },

  async confirmFirstRaceRegistration(reviewToken: string): Promise<RegistrationConfirmResult> {
    const response = await fetch(`${appConfig.apiBaseUrl}/registrations/first-race/confirm`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${requireAccessToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ review_token: reviewToken }),
    });

    if (!response.ok) {
      throw new Error(await readError(response));
    }

    const result = (await response.json()) as RegistrationConfirmApiResponse;
    return {
      id: result.id,
      raceId: result.race_id,
      raceName: result.race_name,
      message: result.message,
    };
  },
};
