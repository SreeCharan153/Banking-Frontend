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

export interface TransferRequest extends AccountBase {
  r: string;
  amount: number;
}

export interface ChangePinRequest extends AccountBase {
  newpin: string;
}

export interface ApiResponse {
  message: string;
}

export interface ApiError {
  detail: string;
}

export interface HistoryEntry {
  id: number;
  account_id: string;
  action: string;
  amount: number;
  timestamp: string;
}

export type HistoryResponse =
  | { history: HistoryEntry[] }    // success
  | { message: string };           // error
