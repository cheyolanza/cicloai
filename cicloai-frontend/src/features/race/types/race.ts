export interface Race {
  id: string;
  name: string;
  date?: string;
  description?: string;
  stravaMapHtml?: string | null;
  inscriptionPrice: number;
  currency: 'BOB' | 'USD';
  paymentQrImage?: string | null;
}
