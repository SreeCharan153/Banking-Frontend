import { API_BASE_URL } from './config';

export class ATMApiClient {

  // No token storage needed anymore
  private async makeAuthRequest<T>(endpoint: string, data: any): Promise<T> {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
      credentials: "include", // ✅ SEND COOKIE AUTOMATICALLY
    });

    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "API failed");
    return json;
  }


  async login(username: string, password: string) {
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);

    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      body: form,
      credentials: "include", // ✅ STORE COOKIE AUTOMATICALLY
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Login failed");

    return data; // cookie is already saved, nothing else to do
  }

  async logout() {
    const res = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });

    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Logout failed");
    return json;
  }

  async createUser(data: { un: string; pas: string; vps: string; role: string }): Promise<{ success: boolean; message: string }> {
  return this.makeAuthRequest("/auth/create-user", data);
}


  async createAccount(data: { h: string; pin: string; vpin: string; mobileno: string; gmail: string }) {
    return this.makeAuthRequest("/account/create", data);
  }

  async deposit(data: { h: string; amount: number; pin: number }) {
    return this.makeAuthRequest("/transaction/deposit", data);
  }

  async withdraw(data: { h: string; amount: number; pin: number }) {
    return this.makeAuthRequest("/transaction/withdraw", data);
  }

  async transfer(data: { h: string; pin: number; toAccount: string; amount: number; }) {
    return this.makeAuthRequest("/transaction/transfer", data);
  }

  async enquiry(data: { h: string; pin: number }) {
    return this.makeAuthRequest("/account/enquiry", data);
  }

  async history(data: { h: string; pin: number }) {
    return this.makeAuthRequest("/account/history", data);
  }

  async changePin(data: { h: string; oldpin: number; newpin: number; vnewpin: number }) {
    return this.makeAuthRequest("/account/change-pin", data);
  }
}

export const atmApi = new ATMApiClient();
