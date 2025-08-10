//const API_BASE_URL = 'http://localhost:8000'; // Update this to your API URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
export class ATMApiClient {
  private async makeRequest<T>(
    endpoint: string,
    data: any,
    method: 'POST' = 'POST'
  ): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'API request failed');
      }

      return result;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  async checkPassword(accountNumber: string, password: string) {
    // Use the check-password endpoint to verify account and password
    const params = new URLSearchParams({
      h: accountNumber,
      pas: password
    });
    
    try {
      const response = await fetch(`${API_BASE_URL}/check-password/?${params}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Authentication failed');
      }

      return result;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  async deposit(data: { h: string; amount: number; pin: number }) {
    return this.makeRequest('/deposit/', { h: data.h, amount: data.amount, pin: data.pin.toString() });
  }

  async withdraw(data: { h: string; amount: number; pin: number }) {
    return this.makeRequest('/withdraw/', { h: data.h, amount: data.amount, pin: data.pin.toString() });
  }

  async createAccount(data: {
    h: string;
    pin: string;
    mobileno: string;
    gmail: string;
  }) {
    return this.makeRequest('/create/', data);
  }

  async updateMobile(data: {
    h: string;
    nmobile: string;
    omobile: string;
  }) {
    return this.makeRequest('/update-mobile/', { h: data.h, nmobile: data.nmobile, omobile: data.omobile });
  }


  async updateEmail(data: {
    h: string;
    nemail: string;
    oemail: string;
  }) {
    return this.makeRequest('/update-email/', { h: data.h, nemail: data.nemail, oemail: data.oemail });
  }

  async transfer(data: { h: string; toAccount: string; amount: number; pin: number }) {
    const transferData = {
      h: data.h,
      r: data.toAccount,
      amount: data.amount,
      pin: data.pin
    };
    return this.makeRequest('/transfor/', transferData);
  }

  async enquiry(data: { h: string; pin: number }) {
    return this.makeRequest('/enquiry/', { h: data.h, pin: data.pin.toString() });
  }

  async changePin(data: { h: string; pin: number; newpin: string }) {
    return this.makeRequest('/change-pin/', { h: data.h, pin: data.pin.toString(), newpin: data.newpin });
  }
}

export const atmApi = new ATMApiClient();