import { API_BASE_URL } from './config';

export class ATMApiClient {

  // No token storage needed anymore
private async makeAuthRequestPost<T>(endpoint: string, data: any,method: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: method,
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (res.status === 401) {
    // optional: trigger front-end logout
    window.location.reload();
    throw new Error("Session expired, login again.");
  }

  const json = await res.json();
  if (!res.ok) throw new Error(json.detail || "API failed");
  return json;
}

async makeAuthRequestGet<T>(endpoint: string, params: Record<string, string | number>): Promise<T> {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  Object.entries(params).forEach(([key, val]) => url.searchParams.append(key, String(val)));

  const res = await fetch(url.toString(), {
    method: "GET",
    credentials: "include",
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "GET request failed");
  }

  return res.json() as Promise<T>;
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

  async createUser(data: { username: string; pas: string; vps: string; role: string }): Promise<{ success: boolean; message: string }> {
    return this.makeAuthRequestPost("/auth/create-user", data,'POST');
}


  async createAccount(data: { holder_name: string; pin: string; vpin: string; mobileno: string; gmail: string }) {
    return this.makeAuthRequestPost("/account/create", data,'POST');
  }

  async deposit(data: { acc_no: string; amount: number; pin: string }) {
    return this.makeAuthRequestPost("/transaction/deposit", data,'POST');
  }

  async withdraw(data: { acc_no: string; amount: number; pin: string }) {
    return this.makeAuthRequestPost("/transaction/withdraw", data,'POST');
  }

  async transfer(data: { acc_no: string; pin: string; rec_acc_no: string; amount: number; }) {
    return this.makeAuthRequestPost("/transaction/transfer", data,'POST');
  }

  async enquiry(data: { acc_no: string; pin: string }) {
    return this.makeAuthRequestPost("/account/enquiry", data,'POST');
  }

  async history(data: { acc_no: string; pin: string }) {
    return this.makeAuthRequestGet(`/history/${data.acc_no}`, { pin: data.pin });
  }

  async changePin(data: { acc_no: string; pin: string; newpin: string; vnewpin: string }) {
    return this.makeAuthRequestPost("/account/change-pin", data,'PUT');
  }

  async updateMobile(data: { acc_no: string; pin: string; omobile: string; nmobile: string }) {
    return this.makeAuthRequestPost("/account/update-mobile", data,'PUT');
  }

  async updateEmail(data: { acc_no: string; pin: string; oemail: string; nemail: string }) {
    return this.makeAuthRequestPost("/account/update-email", data,'PUT');
  }
}

export const atmApi = new ATMApiClient();
