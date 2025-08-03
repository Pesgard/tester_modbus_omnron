import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface User {
	id: number;
	username: string;
	email: string;
	full_name?: string;
	role: 'admin' | 'supervisor' | 'operator' | 'viewer';
	is_active: boolean;
	last_login?: string;
	created_at: string;
}

export interface AuthState {
	isAuthenticated: boolean;
	user: User | null;
	token: string | null;
	loading: boolean;
}

const initialState: AuthState = {
	isAuthenticated: false,
	user: null,
	token: null,
	loading: false
};

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>(initialState);

	return {
		subscribe,
		login: (token: string, user: User) => {
			if (browser) {
				localStorage.setItem('token', token);
				localStorage.setItem('user', JSON.stringify(user));
			}
			set({
				isAuthenticated: true,
				user,
				token,
				loading: false
			});
		},
		logout: () => {
			if (browser) {
				localStorage.removeItem('token');
				localStorage.removeItem('user');
			}
			set(initialState);
		},
		setLoading: (loading: boolean) => {
			update(state => ({ ...state, loading }));
		},
		initializeFromStorage: () => {
			if (browser) {
				const token = localStorage.getItem('token');
				const userStr = localStorage.getItem('user');
				
				if (token && userStr) {
					try {
						const user = JSON.parse(userStr);
						set({
							isAuthenticated: true,
							user,
							token,
							loading: false
						});
					} catch (error) {
						console.error('Error parsing user data:', error);
						// Clear invalid data
						localStorage.removeItem('token');
						localStorage.removeItem('user');
					}
				}
			}
		}
	};
}

export const authStore = createAuthStore();