<script lang="ts">
	import { onMount } from 'svelte';
	import { productionApi } from '$lib/services/api';
	import type { ProductionData } from '$lib/stores/production';

	let historyData = $state<ProductionData[]>([]);
	let isLoading = $state(false);
	let error = $state('');
	let currentPage = $state(1);
	let itemsPerPage = $state(50);
	let totalPages = $state(1);

	// Filter parameters
	let startDate = $state('');
	let endDate = $state('');
	let qualityFilter = $state('');
	let statusFilter = $state('');

	onMount(() => {
		// Set default date range (last 7 days)
		const now = new Date();
		const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
		
		endDate = now.toISOString().split('T')[0];
		startDate = sevenDaysAgo.toISOString().split('T')[0];
		
		loadHistory();
	});

	async function loadHistory() {
		isLoading = true;
		error = '';

		try {
			const params: any = {
				limit: itemsPerPage,
				offset: (currentPage - 1) * itemsPerPage
			};

			if (startDate) params.start_date = startDate;
			if (endDate) params.end_date = endDate;

			const data = await productionApi.getHistory(params);
			
			// Filter client-side for quality and status if specified
			let filteredData = data;
			
			if (qualityFilter) {
				filteredData = filteredData.filter(item => item.quality_status === qualityFilter);
			}
			
			if (statusFilter) {
				filteredData = filteredData.filter(item => item.line_status === statusFilter);
			}

			historyData = filteredData;
			totalPages = Math.max(1, Math.ceil(filteredData.length / itemsPerPage));
			
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load production history';
			historyData = [];
		} finally {
			isLoading = false;
		}
	}

	function handleFilterChange() {
		currentPage = 1;
		loadHistory();
	}

	function changePage(page: number) {
		currentPage = page;
		loadHistory();
	}

	function formatTimestamp(timestamp: string): string {
		return new Date(timestamp).toLocaleString();
	}

	function getStatusBadgeClass(status: string): string {
		switch (status) {
			case 'RUNNING': return 'preset-filled-success';
			case 'STOPPED': return 'preset-filled-surface';
			case 'ERROR': return 'preset-filled-error';
			case 'MAINTENANCE': return 'preset-filled-warning';
			default: return 'preset-filled-surface';
		}
	}

	function getQualityBadgeClass(quality: string): string {
		switch (quality) {
			case 'OK': return 'preset-filled-success';
			case 'NOK': return 'preset-filled-error';
			case 'PENDING': return 'preset-filled-warning';
			default: return 'preset-filled-surface';
		}
	}

	function exportToCSV() {
		const headers = [
			'Timestamp',
			'Product ID',
			'Quality Status',
			'Production Count',
			'Line Status',
			'Error Code',
			'Cycle Time (ms)',
			'Temperature (°C)',
			'Pressure (bar)',
			'Operator ID',
			'Batch ID'
		];

		const csvContent = [
			headers.join(','),
			...historyData.map(item => [
				item.timestamp,
				item.product_id,
				item.quality_status,
				item.production_count,
				item.line_status,
				item.error_code,
				item.cycle_time_ms,
				item.temperature,
				item.pressure,
				item.operator_id,
				item.batch_id
			].join(','))
		].join('\n');

		const blob = new Blob([csvContent], { type: 'text/csv' });
		const url = window.URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `production_history_${new Date().toISOString().split('T')[0]}.csv`;
		a.click();
		window.URL.revokeObjectURL(url);
	}
</script>

<svelte:head>
	<title>Production History - AXME Production System</title>
</svelte:head>

<div class="p-6 space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold">Production History</h1>
			<p class="text-surface-600-400">Historical production data and analytics</p>
		</div>
		
		<button 
			class="btn preset-filled-primary"
			onclick={exportToCSV}
			disabled={historyData.length === 0}
		>
			📄 Export CSV
		</button>
	</div>

	<!-- Filters -->
	<div class="card preset-outlined p-6">
		<h2 class="text-lg font-semibold mb-4">Filters</h2>
		
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
			<div class="space-y-2">
				<label for="startDate" class="label">Start Date</label>
				<input
					id="startDate"
					type="date"
					class="input"
					bind:value={startDate}
					onchange={handleFilterChange}
				/>
			</div>
			
			<div class="space-y-2">
				<label for="endDate" class="label">End Date</label>
				<input
					id="endDate"
					type="date"
					class="input"
					bind:value={endDate}
					onchange={handleFilterChange}
				/>
			</div>
			
			<div class="space-y-2">
				<label for="qualityFilter" class="label">Quality Status</label>
				<select
					id="qualityFilter"
					class="select"
					bind:value={qualityFilter}
					onchange={handleFilterChange}
				>
					<option value="">All</option>
					<option value="OK">OK</option>
					<option value="NOK">NOK</option>
					<option value="PENDING">PENDING</option>
				</select>
			</div>
			
			<div class="space-y-2">
				<label for="statusFilter" class="label">Line Status</label>
				<select
					id="statusFilter"
					class="select"
					bind:value={statusFilter}
					onchange={handleFilterChange}
				>
					<option value="">All</option>
					<option value="RUNNING">RUNNING</option>
					<option value="STOPPED">STOPPED</option>
					<option value="ERROR">ERROR</option>
					<option value="MAINTENANCE">MAINTENANCE</option>
				</select>
			</div>
			
			<div class="space-y-2">
				<label class="label">&nbsp;</label>
				<button 
					class="btn preset-tonal-primary w-full"
					onclick={handleFilterChange}
				>
					🔍 Apply Filters
				</button>
			</div>
		</div>
	</div>

	<!-- Error Message -->
	{#if error}
		<div class="alert preset-filled-error">
			<div class="alert-message">
				<h3 class="h4">Error</h3>
				<p>{error}</p>
			</div>
		</div>
	{/if}

	<!-- Loading State -->
	{#if isLoading}
		<div class="flex items-center justify-center h-64">
			<div class="text-center">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
				<p class="text-surface-600-400">Loading production history...</p>
			</div>
		</div>
	{:else if historyData.length === 0}
		<!-- No Data -->
		<div class="card preset-outlined p-12 text-center">
			<div class="text-6xl mb-4">📊</div>
			<h3 class="text-xl font-bold mb-2">No Production Data Found</h3>
			<p class="text-surface-600-400">
				No production records found for the selected date range and filters.
			</p>
		</div>
	{:else}
		<!-- Data Table -->
		<div class="card preset-outlined overflow-hidden">
			<div class="overflow-x-auto">
				<table class="table table-hover">
					<thead>
						<tr>
							<th>Timestamp</th>
							<th>Product ID</th>
							<th>Quality</th>
							<th>Count</th>
							<th>Status</th>
							<th>Cycle Time</th>
							<th>Temperature</th>
							<th>Pressure</th>
							<th>Batch ID</th>
							<th>Error Code</th>
						</tr>
					</thead>
					<tbody>
						{#each historyData as item}
							<tr>
								<td class="font-mono text-sm">
									{formatTimestamp(item.timestamp)}
								</td>
								<td class="font-mono font-bold">
									{item.product_id}
								</td>
								<td>
									<span class="badge {getQualityBadgeClass(item.quality_status)} text-xs">
										{item.quality_status}
									</span>
								</td>
								<td class="font-mono">
									{item.production_count.toLocaleString()}
								</td>
								<td>
									<span class="badge {getStatusBadgeClass(item.line_status)} text-xs">
										{item.line_status}
									</span>
								</td>
								<td class="font-mono">
									{item.cycle_time_ms}ms
								</td>
								<td class="font-mono">
									{item.temperature}°C
								</td>
								<td class="font-mono">
									{item.pressure} bar
								</td>
								<td class="font-mono text-sm">
									{item.batch_id}
								</td>
								<td class="font-mono" class:text-error-500={item.error_code !== 0}>
									{item.error_code}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>

		<!-- Pagination -->
		{#if totalPages > 1}
			<div class="flex items-center justify-center space-x-2">
				<button 
					class="btn preset-tonal-surface btn-sm"
					disabled={currentPage === 1}
					onclick={() => changePage(currentPage - 1)}
				>
					← Previous
				</button>
				
				<span class="text-sm text-surface-600-400">
					Page {currentPage} of {totalPages}
				</span>
				
				<button 
					class="btn preset-tonal-surface btn-sm"
					disabled={currentPage === totalPages}
					onclick={() => changePage(currentPage + 1)}
				>
					Next →
				</button>
			</div>
		{/if}

		<!-- Summary -->
		<div class="text-center text-sm text-surface-600-400">
			Showing {historyData.length} records
		</div>
	{/if}
</div>