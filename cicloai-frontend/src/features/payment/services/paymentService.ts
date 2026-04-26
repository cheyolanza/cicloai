import type { RegistrationType } from '@/features/agent/types/registration';
import type { PaymentValidationResult } from '@/features/payment/types/payment';

export interface PaymentAmountRequest {
  registrationType: RegistrationType;
  competitorsCount?: number;
  unitPrice: number;
}

export interface PaymentService {
  getStaticQrUrl(): string;
  calculateAmount(request: PaymentAmountRequest): number;
  validateProof(file: File | null): Promise<PaymentValidationResult>;
}

/**
 * Payment boundary for the wizard. The QR is intentionally static in Fase 1;
 * when FastAPI owns payment intent creation, this service should fetch a
 * dynamic QR URL and amount from `/payments/intents` instead of calculating
 * them in the browser.
 */
export const paymentService: PaymentService = {
  getStaticQrUrl(): string {
    return '/images/qr_payment.png';
  },
  calculateAmount({ registrationType, competitorsCount = 1, unitPrice }: PaymentAmountRequest): number {
    const quantity = registrationType === 'bulk' ? competitorsCount : 1;
    return quantity * unitPrice;
  },
  async validateProof(file: File | null): Promise<PaymentValidationResult> {
    await new Promise((resolve) => window.setTimeout(resolve, 500));

    return file
      ? {
          status: 'approved',
          valid: true,
          reference: `MOCK-${Date.now()}`,
          message: 'Comprobante recibido. La validación definitiva se realizará en backend.',
        }
      : {
          status: 'rejected',
          valid: false,
          reference: '',
          message: 'Debes subir un comprobante para continuar.',
        };
  },
};
