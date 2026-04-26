export interface Race {
  id: string;
  name: string;
  date?: string;
  description?: string;
  inscriptionPrice: number;
  currency: 'BOB' | 'USD';
  paymentQrImage?: string | null;
}
