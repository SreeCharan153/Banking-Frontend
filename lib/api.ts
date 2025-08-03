const API_BASE_URL = 'http://localhost:8000'; // Update this to your API URL

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

  async verifyPassword(password: string) {
    const params = new URLSearchParams({ pas: password });
    const response = await fetch(`${API_BASE_URL}/?${params}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.detail || 'Password verification failed');
    }

    return result;
  }

  async deposit(data: { h: string; amount: number; pin: number }) {
    return this.makeRequest('/deposit/', data);
  }

  async withdraw(data: { h: string; amount: number; pin: number }) {
    return this.makeRequest('/withdraw/', data);
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
    pin: number;
    nmobile: string;
    omobile: string;
  }) {
    return this.makeRequest('/update-mobile/', data);
  }

  async updateEmail(data: {
    h: string;
    pin: number;
    nemail: string;
    oemail: string;
  }) {
    return this.makeRequest('/update-email/', data);
  }
}

export const atmApi = new ATMApiClient();