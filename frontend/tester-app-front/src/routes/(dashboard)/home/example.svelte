<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { writable } from 'svelte/store';
	// Skeleton UI Components
	import { AppBar } from '@skeletonlabs/skeleton-svelte';
	// Lucide Icons
	import Activity from '@lucide/svelte/icons/activity';
	import Wifi from '@lucide/svelte/icons/wifi';
	import WifiOff from '@lucide/svelte/icons/wifi-off';
	import TrendingUp from '@lucide/svelte/icons/trending-up';
	import TrendingDown from '@lucide/svelte/icons/trending-down';
	import CheckCircle from '@lucide/svelte/icons/check-circle';
	import XCircle from '@lucide/svelte/icons/x-circle';
	import Clock from '@lucide/svelte/icons/clock';
	import Zap from '@lucide/svelte/icons/zap';
	import Target from '@lucide/svelte/icons/target';
	import BarChart3 from '@lucide/svelte/icons/bar-chart-3';

	// Types
	interface ProductionData {
		totalItems: number;
		processedItems: number;
		goodItems: number;
		badItems: number;
		accuracy: number;
		rate: number; // items per minute
		efficiency: number;
		temperature: number;
		pressure: number;
		vibration: number;
		lastUpdate: Date;
	}

	interface ConnectionStatus {
		isConnected: boolean;
		server: string;
		latency: number;
		lastPing: Date;
	}

	// State
	let isConnected = $state(true);
	let isRunning = $state(false);
	let connectionStatus = $state<ConnectionStatus>({
		isConnected: true,
		server: 'prod-server-01.company.com',
		latency: 45,
		lastPing: new Date()
	});

	let productionData = $state<ProductionData>({
		totalItems: 100,
		processedItems: 30,
		goodItems: 24,
		badItems: 6,
		accuracy: 80,
		rate: 45,
		efficiency: 87,
		temperature: 72.5,
		pressure: 2.4,
		vibration: 0.8,
		lastUpdate: new Date()
	});

	// Simulated real-time data intervals
	let dataInterval: ReturnType<typeof setInterval>;
	let connectionInterval: ReturnType<typeof setInterval>;

	// Functions
	function toggleConnection() {
		isConnected = !isConnected;
		connectionStatus.isConnected = isConnected;
		
		if (isConnected) {
			startDataSimulation();
		} else {
			stopDataSimulation();
		}
	}

	function toggleProduction() {
		isRunning = !isRunning;
		
		if (isRunning && isConnected) {
			startDataSimulation();
		} else {
			stopDataSimulation();
		}
	}

	function startDataSimulation() {
		if (dataInterval) clearInterval(dataInterval);
		
		dataInterval = setInterval(() => {
			if (isConnected && isRunning && productionData.processedItems < productionData.totalItems) {
				// Simulate processing items
				productionData.processedItems = Math.min(
					productionData.processedItems + Math.floor(Math.random() * 3) + 1,
					productionData.totalItems
				);
				
				// Simulate good/bad items ratio (80-95% accuracy)
				const randomAccuracy = 0.8 + Math.random() * 0.15;
				productionData.goodItems = Math.floor(productionData.processedItems * randomAccuracy);
				productionData.badItems = productionData.processedItems - productionData.goodItems;
				productionData.accuracy = Math.round((productionData.goodItems / productionData.processedItems) * 100);
				
				// Simulate other metrics
				productionData.rate = 40 + Math.random() * 20;
				productionData.efficiency = 80 + Math.random() * 15;
				productionData.temperature = 70 + Math.random() * 10;
				productionData.pressure = 2.0 + Math.random() * 1.0;
				productionData.vibration = 0.5 + Math.random() * 1.0;
				productionData.lastUpdate = new Date();
				
				// Simulate connection latency
				connectionStatus.latency = 30 + Math.random() * 40;
				connectionStatus.lastPing = new Date();
			}
		}, 2000); // Update every 2 seconds
	}

	function stopDataSimulation() {
		if (dataInterval) {
			clearInterval(dataInterval);
		}
	}

	// function resetProduction() {
	// 	productionData.processedItems = 0;
	// 	productionData.goodItems = 0;
	// 	productionData.badItems = 0;
	// 	productionData.accuracy = 0;
	// 	productionData.lastUpdate = new Date();
	// }

	function getProgressPercentage() {
		return (productionData.processedItems / productionData.totalItems) * 100;
	}

	function getAccuracyColor(accuracy: number) {
		if (accuracy >= 95) return 'preset-filled-success-500';
		if (accuracy >= 85) return 'preset-filled-warning-500';
		return 'preset-filled-error-500';
	}

	function getEfficiencyColor(efficiency: number) {
		if (efficiency >= 90) return 'preset-filled-success-500';
		if (efficiency >= 75) return 'preset-filled-warning-500';
		return 'preset-filled-error-500';
	}

	function getConnectionLatencyColor(latency: number) {
		if (latency <= 50) return 'text-success-500';
		if (latency <= 100) return 'text-warning-500';
		return 'text-error-500';
	}

	onMount(() => {
		// Simulate periodic connection checks
		connectionInterval = setInterval(() => {
			if (isConnected) {
				connectionStatus.lastPing = new Date();
				// Occasionally simulate connection issues
				if (Math.random() < 0.05) {
					connectionStatus.latency = 150 + Math.random() * 100;
				}
			}
		}, 5000);
		
		// Start with simulation if connected and running
		if (isConnected && isRunning) {
			startDataSimulation();
		}
	});

	onDestroy(() => {
		stopDataSimulation();
		if (connectionInterval) clearInterval(connectionInterval);
	});
</script>

<div class="min-h-screen flex flex-col">
	<!-- App Bar -->
	<AppBar>
		<h1 class="h1">Production Dashboard</h1>
		{#snippet trail()}
			<div class="flex items-center gap-4">
				<!-- Connection Status -->
				<div class="flex items-center gap-2">
					{#if connectionStatus.isConnected}
						<Wifi size={20} class="text-success-500" />
						<span class="text-sm {getConnectionLatencyColor(connectionStatus.latency)}">
							{connectionStatus.latency}ms
						</span>
					{:else}
						<WifiOff size={20} class="text-error-500" />
						<span class="text-sm text-error-500">Offline</span>
					{/if}
				</div>
				
				<!-- Connection Toggle -->
				<button 
					class="btn {isConnected ? 'preset-filled-success' : 'preset-filled-error'} btn-sm"
					onclick={toggleConnection}
				>
					{isConnected ? 'Connected' : 'Disconnected'}
				</button>
			</div>
		{/snippet}
	</AppBar>

	<!-- Main Dashboard -->
	<div class="flex-1 p-6 space-y-6">
		<!-- Status Cards Row -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
			<!-- Production Status -->
			<div class="card p-6 space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="h3">Production Status</h3>
					<div class="flex items-center gap-2">
						{#if isRunning}
							<div class="w-3 h-3 bg-success-500 rounded-full animate-pulse"></div>
							<span class="text-success-500 text-sm font-bold">RUNNING</span>
						{:else}
							<div class="w-3 h-3 bg-error-500 rounded-full"></div>
							<span class="text-error-500 text-sm font-bold">STOPPED</span>
						{/if}
					</div>
				</div>
				<button 
					class="btn {isRunning ? 'preset-filled-error' : 'preset-filled-success'} w-full"
					onclick={toggleProduction}
					disabled={!isConnected}
				>
					{isRunning ? 'Stop Production' : 'Start Production'}
				</button>
			</div>

			<!-- Server Connection -->
			<div class="card p-6 space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="h3">Server</h3>
					{#if connectionStatus.isConnected}
						<CheckCircle size={24} class="text-success-500" />
					{:else}
						<XCircle size={24} class="text-error-500" />
					{/if}
				</div>
				<div class="space-y-2">
					<p class="text-sm opacity-75">{connectionStatus.server}</p>
					<p class="text-xs opacity-60">
						Last ping: {connectionStatus.lastPing.toLocaleTimeString()}
					</p>
				</div>
			</div>

			<!-- Current Rate -->
			<div class="card p-6 space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="h3">Production Rate</h3>
					<Zap size={24} class="text-warning-500" />
				</div>
				<div>
					<p class="text-3xl font-bold">{productionData.rate.toFixed(1)}</p>
					<p class="text-sm opacity-75">items/min</p>
				</div>
			</div>

			<!-- Efficiency -->
			<div class="card p-6 space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="h3">Efficiency</h3>
					<Target size={24} class="text-primary-500" />
				</div>
				<div>
					<p class="text-3xl font-bold">{productionData.efficiency.toFixed(1)}%</p>
					<span class="badge {getEfficiencyColor(productionData.efficiency)} text-xs mt-2">
						{productionData.efficiency >= 85 ? 'Optimal' : productionData.efficiency >= 70 ? 'Good' : 'Poor'}
					</span>
				</div>
			</div>
		</div>

		<!-- Progress and Quality Section -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- Production Progress -->
			<div class="card p-6 space-y-6">
				<div class="flex items-center justify-between">
					<h2 class="h2">Production Progress</h2>
					<!-- <button 
						class="btn preset-tonal btn-sm" 
						onclick={resetProduction}
						disabled={isRunning}
					>
						Reset
					</button> -->
				</div>
				
				<!-- Overall Progress -->
				<div class="space-y-4">
					<div class="flex justify-between items-center">
						<span class="font-bold">Overall Progress</span>
						<span class="text-sm opacity-75">
							{productionData.processedItems} / {productionData.totalItems}
						</span>
					</div>
					<div class="w-full bg-surface-300-600 rounded-full h-4">
						<div 
							class="bg-primary-500 h-4 rounded-full transition-all duration-300"
							style="width: {getProgressPercentage()}%"
						></div>
					</div>
					<p class="text-center text-sm opacity-75">
						{getProgressPercentage().toFixed(1)}% Complete
					</p>
				</div>

				<!-- Item Breakdown -->
				<div class="grid grid-cols-2 gap-4">
					<div class="text-center p-4 bg-success-500/10 rounded-lg">
						<CheckCircle size={32} class="text-success-500 mx-auto mb-2" />
						<p class="text-2xl font-bold text-success-500">{productionData.goodItems}</p>
						<p class="text-sm opacity-75">Good Items</p>
					</div>
					<div class="text-center p-4 bg-error-500/10 rounded-lg">
						<XCircle size={32} class="text-error-500 mx-auto mb-2" />
						<p class="text-2xl font-bold text-error-500">{productionData.badItems}</p>
						<p class="text-sm opacity-75">Bad Items</p>
					</div>
				</div>
			</div>

			<!-- Quality Metrics -->
			<div class="card p-6 space-y-6">
				<div class="flex items-center justify-between">
					<h2 class="h2">Quality Metrics</h2>
					<BarChart3 size={24} class="text-primary-500" />
				</div>

				<!-- Accuracy -->
				<div class="space-y-4">
					<div class="flex justify-between items-center">
						<span class="font-bold">Accuracy Rate</span>
						<span class="text-2xl font-bold">{productionData.accuracy}%</span>
					</div>
					<div class="w-full bg-surface-300-600 rounded-full h-4">
						<div 
							class="h-4 rounded-full transition-all duration-300 {productionData.accuracy >= 95 ? 'bg-success-500' : 
								   productionData.accuracy >= 85 ? 'bg-warning-500' : 'bg-error-500'}"
							style="width: {productionData.accuracy}%"
						></div>
					</div>
					<div class="flex justify-between text-sm opacity-75">
						<span>Target: 95%</span>
						<span class="{productionData.accuracy >= 95 ? 'text-success-500' : 
									   productionData.accuracy >= 85 ? 'text-warning-500' : 'text-error-500'}">
							{productionData.accuracy >= 95 ? 'Excellent' : 
							 productionData.accuracy >= 85 ? 'Good' : 'Needs Improvement'}
						</span>
					</div>
				</div>

				<!-- Quality Trend -->
				<div class="grid grid-cols-3 gap-4 pt-4 border-t border-surface-300-600">
					<div class="text-center">
						<TrendingUp size={24} class="text-success-500 mx-auto mb-1" />
						<p class="text-sm font-bold">+2.3%</p>
						<p class="text-xs opacity-60">vs Yesterday</p>
					</div>
					<div class="text-center">
						<TrendingDown size={24} class="text-error-500 mx-auto mb-1" />
						<p class="text-sm font-bold">-0.8%</p>
						<p class="text-xs opacity-60">vs Last Week</p>
					</div>
					<div class="text-center">
						<Target size={24} class="text-primary-500 mx-auto mb-1" />
						<p class="text-sm font-bold">87.2%</p>
						<p class="text-xs opacity-60">Monthly Avg</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</div> 