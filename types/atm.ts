export interface AccountBase {
  h: string;
  pin?: number;
}

export interface TransactionRequest extends AccountBase {
  amount: number;
}

export interface CreateAccountRequest {
  h: string;
  pin: string;
  mobileno: string;
  gmail: string;
}

export interface UpdateMobileRequest extends AccountBase {
  nmobile: string;
  omobile: string;
}

export interface UpdateEmailRequest extends AccountBase {
  nemail: string;
  oemail: string;
}

export interface ApiResponse {
  message: string;
}

export interface ApiError {
  detail: string;
}