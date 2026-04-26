export interface ServiceResponse<T> {
  data: T;
  ok: boolean;
  message?: string;
}
