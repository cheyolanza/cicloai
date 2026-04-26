export interface PaymentValidationResult {
  status: 'approved' | 'rejected';
  valid: boolean;
  reference: string;
  message: string;
}
