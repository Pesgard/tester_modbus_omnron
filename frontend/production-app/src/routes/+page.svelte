<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { productionStore } from '$lib/stores/production';
	import { authStore } from '$lib/stores/auth';
	import { productionApi } from '$lib/services/api';
	import { getWebSocketInstance } from '$lib/services/websocket';
	import ConnectionStatus from '$lib/components/ConnectionStatus.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';

	let refreshInterval = $state<number | null>(null);

	onMount(async () => {
		// Initial data load
		await loadInitialData();

		// Refresh data every 30 seconds
		refreshInterval = window.setInterval(loadStats, 30000);
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	async function loadInitialData() {
		try {
			productionStore.setLoading(true);
			
			// Load current data and stats in parallel
			const [currentData, stats] = await Promise.all([
				productionApi.getCurrentData().catch(() => null),
				productionApi.getStats().catch(() => null)
			]);

			if (currentData) {
				productionStore.setCurrentData(currentData);
			}
			
			if (stats) {
				productionStore.setStats(stats);
			}
		} catch (error) {
			console.error('Error loading initial data:', error);
			productionStore.setError('Failed to load production data');
		} finally {
			productionStore.setLoading(false);
		}
	}

	async function loadStats() {
		try {
			const stats = await productionApi.getStats();
			productionStore.setStats(stats);
		} catch (error) {
			console.error('Error loading stats:', error);
		}
	}

	function getStatusColor(status: string): string {
		switch (status) {
			case 'RUNNING': return 'preset-filled-success';
			case 'STOPPED': return 'preset-filled-surface';
			case 'ERROR': return 'preset-filled-error';
			case 'MAINTENANCE': return 'preset-filled-warning';
			default: return 'preset-filled-surface';
		}
	}

	function getQualityColor(quality: string): string {
		switch (quality) {
			case 'OK': return 'preset-filled-success';
			case 'NOK': return 'preset-filled-error';
			case 'PENDING': return 'preset-filled-warning';
			default: return 'preset-filled-surface';
		}
	}

	function formatTimestamp(timestamp: string): string {
		return new Date(timestamp).toLocaleString();
	}
</script>

<svelte:head>
	<title>Dashboard - AXME Production System</title>
</svelte:head>

<div class="p-6 space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold">Production Dashboard</h1>
			<p class="text-surface-600-400">Real-time monitoring of production line</p>
		</div>
		
		<!-- Connection Status -->
		<ConnectionStatus />
	</div>

	<!-- Error Alert -->
	{#if $productionStore.error}
		<div class="alert preset-filled-error">
			<div class="alert-message">
				<h3 class="h4">Error</h3>
				<p>{$productionStore.error}</p>
			</div>
		</div>
	{/if}

	<!-- Loading State -->
	{#if $productionStore.loading}
		<div class="flex items-center justify-center h-64">
			<div class="text-center">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
				<p class="text-surface-600-400">Loading production data...</p>
			</div>
		</div>
	{:else}
		<!-- Production Stats Grid -->
		{#if $productionStore.stats}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
				<MetricCard
					title="Total Products"
					value={$productionStore.stats.total_products}
					icon="📦"
				/>

				<MetricCard
					title="Quality Rate"
					value="{$productionStore.stats.quality_rate_percentage.toFixed(1)}%"
					valueClass="text-success-500"
					icon="✅"
				/>

				<MetricCard
					title="Avg Cycle Time"
					value="{$productionStore.stats.average_cycle_time_ms.toLocaleString()}ms"
					icon="⏱️"
				/>

				<MetricCard
					title="Last Update"
					value={formatTimestamp($productionStore.stats.last_update)}
					icon="🔄"
				/>
			</div>
		{/if}

		<!-- Current Production Data -->
		{#if $productionStore.currentData}
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<!-- Current Status Card -->
				<div class="card preset-outlined p-6">
					<h2 class="text-xl font-bold mb-4">Current Production Status</h2>
					
					<div class="space-y-4">
						<div class="flex items-center justify-between">
							<span class="text-surface-600-400">Product ID:</span>
							<span class="font-mono font-bold">{$productionStore.currentData.product_id}</span>
						</div>
						
						<div class="flex items-center justify-between">
							<span class="text-surface-600-400">Line Status:</span>
							<span class="badge {getStatusColor($productionStore.currentData.line_status)}">
								{$productionStore.currentData.line_status}
							</span>
						</div>
						
						<div class="flex items-center justify-between">
							<span class="text-surface-600-400">Quality:</span>
							<span class="badge {getQualityColor($productionStore.currentData.quality_status)}">
								{$productionStore.currentData.quality_status}
							</span>
						</div>
						
						<div class="flex items-center justify-between">
							<span class="text-surface-600-400">Production Count:</span>
							<span class="font-bold">{$productionStore.currentData.production_count.toLocaleString()}</span>
						</div>
						
						<div class="flex items-center justify-between">
							<span class="text-surface-600-400">Cycle Time:</span>
							<span class="font-mono">{$productionStore.currentData.cycle_time_ms}ms</span>
						</div>
						
						<div class="flex items-center justify-between">
							<span class="text-surface-600-400">Batch ID:</span>
							<span class="font-mono text-sm">{$productionStore.currentData.batch_id}</span>
						</div>
					</div>
				</div>

				<!-- Process Parameters Card -->
				<div class="card preset-outlined p-6">
					<h2 class="text-xl font-bold mb-4">Process Parameters</h2>
					
					<div class="space-y-4">
						<div class="flex items-center justify-between">
							<span class="text-surface-600-400">Temperature:</span>
							<span class="font-mono">{$productionStore.currentData.temperature}°C</span>
						</div>
						
						<div class="flex items-center justify-between">
							<span class="text-surface-600-400">Pressure:</span>
							<span class="font-mono">{$productionStore.currentData.pressure} bar</span>
						</div>
						
						<div class="flex items-center justify-between">
							<span class="text-surface-600-400">Operator ID:</span>
							<span class="font-mono">{$productionStore.currentData.operator_id}</span>
						</div>
						
						<div class="flex items-center justify-between">
							<span class="text-surface-600-400">Error Code:</span>
							<span class="font-mono" class:text-error-500={$productionStore.currentData.error_code !== 0}>
								{$productionStore.currentData.error_code}
							</span>
						</div>
						
						<div class="border-t border-surface-300-700 pt-4">
							<span class="text-surface-600-400 text-sm">Last Updated:</span>
							<br>
							<span class="text-sm font-mono">{formatTimestamp($productionStore.currentData.timestamp)}</span>
						</div>
					</div>
				</div>
			</div>
		{:else}
			<!-- No Data Available -->
			<div class="card preset-outlined p-12 text-center">
				<div class="text-6xl mb-4">📊</div>
				<h3 class="text-xl font-bold mb-2">No Production Data Available</h3>
				<p class="text-surface-600-400 mb-4">
					Waiting for data from the production line. Make sure the Modbus server is running.
				</p>
				<button 
					class="btn preset-filled-primary"
					onclick={loadInitialData}
				>
					Refresh Data
				</button>
			</div>
		{/if}
	{/if}
</div>