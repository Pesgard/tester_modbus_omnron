import { writable } from 'svelte/store';

export interface ProductionData {
	timestamp: string;
	product_id: number;
	quality_status: 'OK' | 'NOK' | 'PENDING';
	production_count: number;
	line_status: 'STOPPED' | 'RUNNING' | 'ERROR' | 'MAINTENANCE';
	error_code: number;
	cycle_time_ms: number;
	temperature: number;
	pressure: number;
	operator_id: number;
	batch_id: string;
}

export interface ProductionStats {
	total_products: number;
	quality_ok_count: number;
	quality_nok_count: number;
	quality_pending_count: number;
	quality_rate_percentage: number;
	average_cycle_time_ms: number;
	last_update: string;
}

export interface ProductionState {
	currentData: ProductionData | null;
	stats: ProductionStats | null;
	history: ProductionData[];
	loading: boolean;
	error: string | null;
	connectionStatus: 'connected' | 'disconnected' | 'connecting';
}

const initialState: ProductionState = {
	currentData: null,
	stats: null,
	history: [],
	loading: false,
	error: null,
	connectionStatus: 'disconnected'
};

function createProductionStore() {
	const { subscribe, set, update } = writable<ProductionState>(initialState);

	return {
		subscribe,
		setCurrentData: (data: ProductionData) => {
			update(state => ({
				...state,
				currentData: data,
				error: null
			}));
		},
		setStats: (stats: ProductionStats) => {
			update(state => ({
				...state,
				stats,
				error: null
			}));
		},
		setHistory: (history: ProductionData[]) => {
			update(state => ({
				...state,
				history,
				error: null
			}));
		},
		addToHistory: (data: ProductionData) => {
			update(state => ({
				...state,
				history: [data, ...state.history].slice(0, 1000) // Keep last 1000 records
			}));
		},
		setLoading: (loading: boolean) => {
			update(state => ({ ...state, loading }));
		},
		setError: (error: string | null) => {
			update(state => ({ ...state, error }));
		},
		setConnectionStatus: (status: 'connected' | 'disconnected' | 'connecting') => {
			update(state => ({ ...state, connectionStatus: status }));
		},
		reset: () => {
			set(initialState);
		}
	};
}

export const productionStore = createProductionStore();