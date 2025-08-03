import { authStore } from '$lib/stores/auth';
import { get } from 'svelte/store';
import type { User } from '$lib/stores/auth';
import type { ProductionData, ProductionStats } from '$lib/stores/production';

// Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Auth interfaces
export interface LoginRequest {
	username: string;
	password: string;
}

export interface LoginResponse {
	access_token: string;
	token_type: string;
	user: User;
}

export interface ApiError {
	detail: string;
}

// Utility function to get auth headers
function getAuthHeaders(): Record<string, string> {
	const auth = get(authStore);
	const headers: Record<string, string> = {
		'Content-Type': 'application/json'
	};
	
	if (auth.token) {
		headers.Authorization = `Bearer ${auth.token}`;
	}
	
	return headers;
}

// Generic API request function
async function apiRequest<T>(
	endpoint: string,
	options: RequestInit = {}
): Promise<T> {
	const url = `${API_BASE_URL}${endpoint}`;
	
	const response = await fetch(url, {
		...options,
		headers: {
			...getAuthHeaders(),
			...options.headers
		}
	});

	if (!response.ok) {
		let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
		
		try {
			const errorData: ApiError = await response.json();
			errorMessage = errorData.detail || errorMessage;
		} catch {
			// Use default error message if JSON parsing fails
		}
		
		throw new Error(errorMessage);
	}

	return response.json();
}

// Authentication API
export const authApi = {
	async login(credentials: LoginRequest): Promise<LoginResponse> {
		console.log('login', credentials);
		// const formData = new FormData();
		// formData.append('username', credentials.username);
		// formData.append('password', credentials.password);

		console.log(JSON.stringify(credentials));

		const response = await fetch(`${API_BASE_URL}/auth/login`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(credentials)
		});

		console.log('response', response);

		if (!response.ok) {
			let errorMessage = 'Login failed';
			try {
				const errorData: ApiError = await response.json();
				errorMessage = errorData.detail || errorMessage;
			} catch {
				// Use default error message
			}
			throw new Error(errorMessage);
		}

		return response.json();
	},

	async getCurrentUser(): Promise<User> {
		return apiRequest<User>('/auth/me');
	}
};

// Production API
export const productionApi = {
	async getCurrentData(): Promise<ProductionData> {
		return apiRequest<ProductionData>('/production/current');
	},

	async getStats(): Promise<ProductionStats> {
		return apiRequest<ProductionStats>('/production/stats');
	},

	async getHistory(params?: {
		start_date?: string;
		end_date?: string;
		limit?: number;
		offset?: number;
	}): Promise<ProductionData[]> {
		const searchParams = new URLSearchParams();
		
		if (params?.start_date) searchParams.append('start_date', params.start_date);
		if (params?.end_date) searchParams.append('end_date', params.end_date);
		if (params?.limit) searchParams.append('limit', params.limit.toString());
		if (params?.offset) searchParams.append('offset', params.offset.toString());

		const endpoint = `/production/history${searchParams.toString() ? `?${searchParams}` : ''}`;
		return apiRequest<ProductionData[]>(endpoint);
	},

	async startNewBatch(batchId: string): Promise<{ message: string; batch_id: string }> {
		return apiRequest('/production/batch/new', {
			method: 'POST',
			body: JSON.stringify({ batch_id: batchId })
		});
	}
};

// Admin API
export const adminApi = {
	async getUsers(): Promise<User[]> {
		return apiRequest<User[]>('/admin/users');
	},

	async createUser(userData: {
		username: string;
		email: string;
		password: string;
		full_name?: string;
		role: 'admin' | 'supervisor' | 'operator' | 'viewer';
	}): Promise<User> {
		return apiRequest<User>('/admin/users', {
			method: 'POST',
			body: JSON.stringify(userData)
		});
	}
};

// System API
export const systemApi = {
	async getHealth(): Promise<{ status: string; timestamp: string }> {
		return apiRequest<{ status: string; timestamp: string }>('/system/health');
	},

	async getDebugData(): Promise<any> {
		return apiRequest<any>('/system/debug/recent-data');
	}
};