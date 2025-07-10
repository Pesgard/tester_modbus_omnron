
<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	// Skeleton UI Components
	import { AppBar, Modal } from '@skeletonlabs/skeleton-svelte';
	// Lucide Icons
	import Activity from '@lucide/svelte/icons/activity';
	import Wifi from '@lucide/svelte/icons/wifi';
	import WifiOff from '@lucide/svelte/icons/wifi-off';
	import Filter from '@lucide/svelte/icons/filter';
	import Download from '@lucide/svelte/icons/download';
	import Search from '@lucide/svelte/icons/search';
	import Eye from '@lucide/svelte/icons/eye';
	import AlertTriangle from '@lucide/svelte/icons/alert-triangle';
	import Package from '@lucide/svelte/icons/package';
	import Clock from '@lucide/svelte/icons/clock';
	import TrendingUp from '@lucide/svelte/icons/trending-up';
	import X from '@lucide/svelte/icons/x';
	import Calendar from '@lucide/svelte/icons/calendar';
	import User from '@lucide/svelte/icons/user';
	import Building from '@lucide/svelte/icons/building';

	// Types
	interface LackOrder {
		id: string;
		lackType: string;
		description: string;
		totalItemsNeeded: number;
		itemsProduced: number;
		status: 'open' | 'in_progress' | 'finished';
		priority: 'low' | 'medium' | 'high';
		department: string;
		productionLine: string;
		targetCompletionDate: Date;
		createdAt: Date;
		assignedTo?: string;
		estimatedHours: number;
	}

	interface ConnectionStatus {
		isConnected: boolean;
		server: string;
		latency: number;
		lastPing: Date;
	}

	interface LackSummary {
		totalLacks: number;
		openLacks: number;
		inProgressLacks: number;
		finishedLacks: number;
		totalItemsNeeded: number;
		totalItemsProduced: number;
		averageProgress: number;
	}

	// State
	let isConnected = $state(true);
	let connectionStatus = $state<ConnectionStatus>({
		isConnected: true,
		server: 'prod-server-01.company.com',
		latency: 45,
		lastPing: new Date()
	});

	let showLackModal = $state(false);
	let selectedLack: LackOrder | null = $state(null);
	let searchTerm = $state('');
	let statusFilter = $state('all');
	let priorityFilter = $state('all');
	let departmentFilter = $state('all');

	// Sample lacks data
	let lacks = $state<LackOrder[]>([
		{
			id: '1',
			lackType: 'Gear Components Shortage',
			description: 'Critical shortage of precision gears for Assembly Line A. Need high-quality steel gears with specific tolerances for automotive transmission systems.',
			totalItemsNeeded: 150,
			itemsProduced: 45,
			status: 'in_progress',
			priority: 'high',
			department: 'Manufacturing',
			productionLine: 'Line A',
			targetCompletionDate: new Date('2024-02-15'),
			createdAt: new Date('2024-01-15'),
			assignedTo: 'John Doe',
			estimatedHours: 24
		},
		{
			id: '2',
			lackType: 'Electronic Sensors Deficiency',
			description: 'Temperature sensors running low for quality control stations. Critical for maintaining product quality standards.',
			totalItemsNeeded: 75,
			itemsProduced: 25,
			status: 'in_progress',
			priority: 'medium',
			department: 'Quality Control',
			productionLine: 'Line B',
			targetCompletionDate: new Date('2024-02-10'),
			createdAt: new Date('2024-01-14'),
			assignedTo: 'Jane Smith',
			estimatedHours: 16
		},
		{
			id: '3',
			lackType: 'Calibration Tools Missing',
			description: 'Precision measurement tools needed for equipment calibration and maintenance procedures.',
			totalItemsNeeded: 20,
			itemsProduced: 20,
			status: 'finished',
			priority: 'low',
			department: 'Maintenance',
			productionLine: 'Line C',
			targetCompletionDate: new Date('2024-01-20'),
			createdAt: new Date('2024-01-10'),
			assignedTo: 'Mike Johnson',
			estimatedHours: 8
		},
		{
			id: '4',
			lackType: 'Safety Equipment Shortage',
			description: 'Personal protective equipment running low. Critical for worker safety compliance and operational standards.',
			totalItemsNeeded: 200,
			itemsProduced: 50,
			status: 'in_progress',
			priority: 'high',
			department: 'Safety',
			productionLine: 'All Lines',
			targetCompletionDate: new Date('2024-02-05'),
			createdAt: new Date('2024-01-12'),
			assignedTo: 'Sarah Wilson',
			estimatedHours: 32
		},
		{
			id: '5',
			lackType: 'Hydraulic Parts Deficiency',
			description: 'Hydraulic system components needed for press machinery maintenance and optimal performance.',
			totalItemsNeeded: 30,
			itemsProduced: 12,
			status: 'open',
			priority: 'medium',
			department: 'Hydraulics',
			productionLine: 'Line D',
			targetCompletionDate: new Date('2024-02-20'),
			createdAt: new Date('2024-01-18'),
			assignedTo: 'Tom Brown',
			estimatedHours: 20
		},
		{
			id: '6',
			lackType: 'Control System Modules',
			description: 'Advanced control modules for automation systems. Essential for maintaining production efficiency and precision.',
			totalItemsNeeded: 15,
			itemsProduced: 0,
			status: 'open',
			priority: 'high',
			department: 'Automation',
			productionLine: 'Line A',
			targetCompletionDate: new Date('2024-02-08'),
			createdAt: new Date('2024-01-20'),
			assignedTo: 'Alex Garcia',
			estimatedHours: 40
		}
	]);

	// Simulated real-time data intervals
	let connectionInterval: ReturnType<typeof setInterval>;

	// Computed properties
	let filteredLacks = $derived(
		lacks.filter(lack => {
			const matchesSearch = lack.lackType.toLowerCase().includes(searchTerm.toLowerCase()) ||
							   lack.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
							   lack.department.toLowerCase().includes(searchTerm.toLowerCase());
			
			const matchesStatus = statusFilter === 'all' || lack.status === statusFilter;
			const matchesPriority = priorityFilter === 'all' || lack.priority === priorityFilter;
			const matchesDepartment = departmentFilter === 'all' || lack.department === departmentFilter;
			
			return matchesSearch && matchesStatus && matchesPriority && matchesDepartment;
		})
	);

	let lackSummary = $derived<LackSummary>({
		totalLacks: lacks.length,
		openLacks: lacks.filter(l => l.status === 'open').length,
		inProgressLacks: lacks.filter(l => l.status === 'in_progress').length,
		finishedLacks: lacks.filter(l => l.status === 'finished').length,
		totalItemsNeeded: lacks.reduce((sum, l) => sum + l.totalItemsNeeded, 0),
		totalItemsProduced: lacks.reduce((sum, l) => sum + l.itemsProduced, 0),
		averageProgress: lacks.reduce((sum, l) => sum + l.totalItemsNeeded, 0) > 0 
			? (lacks.reduce((sum, l) => sum + l.itemsProduced, 0) / lacks.reduce((sum, l) => sum + l.totalItemsNeeded, 0)) * 100 
			: 0
	});

	let uniqueDepartments = $derived(
		[...new Set(lacks.map(l => l.department))]
	);

	// Functions
	function toggleConnection() {
		isConnected = !isConnected;
		connectionStatus.isConnected = isConnected;
	}

	function getConnectionLatencyColor(latency: number) {
		if (latency <= 50) return 'text-success-500';
		if (latency <= 100) return 'text-warning-500';
		return 'text-error-500';
	}

	function getPriorityColor(priority: string) {
		switch (priority) {
			case 'high': return 'preset-filled-error-500';
			case 'medium': return 'preset-filled-warning-500';
			case 'low': return 'preset-filled-success-500';
			default: return 'preset-filled-surface-500';
		}
	}

	function getStatusColor(status: string) {
		switch (status) {
			case 'open': return 'preset-filled-warning-500';
			case 'in_progress': return 'preset-filled-primary-500';
			case 'finished': return 'preset-filled-success-500';
			default: return 'preset-filled-surface-500';
		}
	}

	function getProgressColor(progress: number) {
		if (progress >= 80) return 'bg-success-500';
		if (progress >= 50) return 'bg-warning-500';
		return 'bg-error-500';
	}

	function openLackDetails(lack: LackOrder) {
		selectedLack = lack;
		showLackModal = true;
	}

	function exportToCSV() {
		const headers = [
			'ID', 'Lack Type', 'Description', 'Total Items Needed', 'Items Produced', 
			'Progress %', 'Status', 'Priority', 'Department', 'Production Line', 
			'Target Completion', 'Created', 'Assigned To', 'Estimated Hours'
		];

		const csvData = filteredLacks.map(lack => [
			lack.id,
			`"${lack.lackType.replace(/"/g, '""')}"`,
			`"${lack.description.replace(/"/g, '""')}"`,
			lack.totalItemsNeeded,
			lack.itemsProduced,
			Math.round((lack.itemsProduced / lack.totalItemsNeeded) * 100),
			lack.status,
			lack.priority,
			lack.department,
			lack.productionLine,
			lack.targetCompletionDate.toISOString().split('T')[0],
			lack.createdAt.toISOString().split('T')[0],
			lack.assignedTo || 'Unassigned',
			lack.estimatedHours
		]);

		const csvContent = [headers, ...csvData]
			.map(row => row.join(','))
			.join('\n');

		const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
		const link = document.createElement('a');
		const url = URL.createObjectURL(blob);
		link.setAttribute('href', url);
		link.setAttribute('download', `lacks_export_${new Date().toISOString().split('T')[0]}.csv`);
		link.style.visibility = 'hidden';
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}

	function clearFilters() {
		searchTerm = '';
		statusFilter = 'all';
		priorityFilter = 'all';
		departmentFilter = 'all';
	}

	function getTimelineStatus(targetDate: Date) {
		const now = new Date();
		const diff = targetDate.getTime() - now.getTime();
		const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
		
		if (days < 0) return { text: `${Math.abs(days)} days overdue`, color: 'text-error-500' };
		if (days === 0) return { text: 'Due today', color: 'text-warning-500' };
		if (days <= 3) return { text: `${days} days left`, color: 'text-warning-500' };
		return { text: `${days} days left`, color: 'text-success-500' };
	}

	function viewLackDetails(lack: LackOrder) {
		selectedLack = lack;
		showLackModal = true;
	}



	onMount(() => {
		// Simulate periodic connection checks
		connectionInterval = setInterval(() => {
			if (isConnected) {
				connectionStatus.lastPing = new Date();
				connectionStatus.latency = 30 + Math.random() * 40;
			}
		}, 5000);
	});

	onDestroy(() => {
		if (connectionInterval) clearInterval(connectionInterval);
	});
</script>

<div class="min-h-screen flex flex-col">
	<!-- App Bar -->
	<AppBar>
		{#snippet lead()}
			<Package size={24} class="text-primary-500" />
		{/snippet}
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
		{#snippet headline()}
			<h1 class="h1">Lacks Dashboard</h1>
		{/snippet}
	</AppBar>

	<!-- Main Dashboard -->
	<div class="flex-1 p-6 space-y-6 overflow-auto">
		<!-- Summary Cards -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			<!-- Total Lacks -->
			<div class="card p-6 space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="h3">Total Lacks</h3>
					<AlertTriangle size={24} class="text-warning-500" />
				</div>
				<div>
					<p class="text-3xl font-bold">{lackSummary.totalLacks}</p>
					<div class="flex gap-2 text-sm mt-2">
						<span class="badge preset-filled-error-500 text-xs">{lackSummary.openLacks} Open</span>
						<span class="badge preset-filled-primary-500 text-xs">{lackSummary.inProgressLacks} In Progress</span>
						<span class="badge preset-filled-success-500 text-xs">{lackSummary.finishedLacks} Finished</span>
					</div>
				</div>
			</div>

			<!-- Items Progress -->
			<div class="card p-6 space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="h3">Items Progress</h3>
					<TrendingUp size={24} class="text-primary-500" />
				</div>
				<div>
					<p class="text-3xl font-bold">{lackSummary.totalItemsProduced}</p>
					<p class="text-sm opacity-75">of {lackSummary.totalItemsNeeded} needed</p>
					<div class="w-full bg-surface-300-600 rounded-full h-3 mt-2">
						<div 
							class="h-3 rounded-full transition-all duration-300 {getProgressColor(lackSummary.averageProgress)}"
							style="width: {lackSummary.averageProgress}%"
						></div>
					</div>
					<p class="text-sm opacity-60 mt-1">{lackSummary.averageProgress.toFixed(1)}% Complete</p>
				</div>
			</div>

			<!-- Average Progress -->
			<div class="card p-6 space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="h3">Avg Progress</h3>
					<Activity size={24} class="text-primary-500" />
				</div>
				<div>
					<p class="text-3xl font-bold">{lackSummary.averageProgress.toFixed(1)}%</p>
					<p class="text-sm opacity-75">Across all lacks</p>
				</div>
			</div>
		</div>

		<!-- Filters and Search -->
		<div class="card p-6">
			<div class="flex flex-wrap gap-4 items-center justify-between">
				<div class="flex flex-wrap gap-4 items-center">
					<!-- Search -->
					<div class="relative">
						<Search size={16} class="absolute left-3 top-1/2 transform -translate-y-1/2 opacity-50" />
						<input 
							class="input pl-10 w-64" 
							type="text" 
							placeholder="Search lacks..."
							bind:value={searchTerm}
						/>
					</div>

					<!-- Status Filter -->
					<select class="select w-40" bind:value={statusFilter}>
						<option value="all">All Status</option>
						<option value="open">Open</option>
						<option value="in_progress">In Progress</option>
						<option value="finished">Finished</option>
					</select>

					<!-- Priority Filter -->
					<select class="select w-40" bind:value={priorityFilter}>
						<option value="all">All Priority</option>
						<option value="high">High</option>
						<option value="medium">Medium</option>
						<option value="low">Low</option>
					</select>

					<!-- Department Filter -->
					<select class="select w-48" bind:value={departmentFilter}>
						<option value="all">All Departments</option>
						{#each uniqueDepartments as dept}
							<option value={dept}>{dept}</option>
						{/each}
					</select>

					<!-- Clear Filters -->
					<button class="btn preset-tonal btn-sm" onclick={clearFilters}>
						<Filter size={16} />
						Clear Filters
					</button>
				</div>

				<!-- Export -->
				<button class="btn preset-filled btn-sm" onclick={exportToCSV}>
					<Download size={16} />
					Export CSV
				</button>
			</div>

			<div class="mt-4 text-sm opacity-75">
				Showing {filteredLacks.length} of {lacks.length} lacks
			</div>
		</div>

		<!-- Lacks Table -->
		<div class="card p-6">
			<div class="table-wrap">
				<table class="table">
					<thead>
						<tr>
							<th>Lack Details</th>
							<th>Progress</th>
							<th>Status</th>
							<th>Priority</th>
							<th>Department</th>
							<th>Timeline</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						{#each filteredLacks as lack}
							<tr class="hover:preset-tonal">
								<td>
									<div class="space-y-1">
										<p class="font-bold">{lack.lackType}</p>
										<p class="text-sm opacity-60 max-w-xs truncate">{lack.description}</p>
										<p class="text-xs opacity-50">Line: {lack.productionLine}</p>
									</div>
								</td>
								<td>
									<div class="space-y-2">
										<div class="flex justify-between text-xs">
											<span>{lack.itemsProduced}</span>
											<span>{lack.totalItemsNeeded}</span>
										</div>
										<div class="w-full bg-surface-300-600 rounded-full h-2">
											<div 
												class="h-2 rounded-full transition-all duration-300 {getProgressColor((lack.itemsProduced / lack.totalItemsNeeded) * 100)}"
												style="width: {(lack.itemsProduced / lack.totalItemsNeeded) * 100}%"
											></div>
										</div>
										<p class="text-xs opacity-60 text-center">
											{Math.round((lack.itemsProduced / lack.totalItemsNeeded) * 100)}%
										</p>
									</div>
								</td>
								<td>
									<span class="badge {getStatusColor(lack.status)} text-xs">
										{lack.status.replace('_', ' ')}
									</span>
								</td>
								<td>
									<span class="badge {getPriorityColor(lack.priority)} text-xs">
										{lack.priority}
									</span>
								</td>
								<td>
									<div class="space-y-1">
										<p class="font-medium text-sm">{lack.department}</p>
										<p class="text-xs opacity-60">{lack.assignedTo || 'Unassigned'}</p>
									</div>
								</td>
								<td>
									<div class="space-y-1">
										<p class="text-sm font-medium">{getTimelineStatus(lack.targetCompletionDate).text}</p>
										<p class="text-xs opacity-60">Due: {lack.targetCompletionDate.toLocaleDateString()}</p>
									</div>
								</td>
								<td>
									<button 
										class="btn preset-filled-primary btn-sm"
										onclick={() => viewLackDetails(lack)}
									>
										<Eye size={14} />
										<span>View</span>
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	</div>
</div>

<!-- Lack Details Modal -->
<Modal
	open={showLackModal}
	onOpenChange={(e) => (showLackModal = e.open)}
	contentBase="card bg-surface-100-900 p-6 space-y-6 shadow-xl max-w-4xl max-h-[90vh] overflow-auto"
	backdropClasses="backdrop-blur-sm"
>
	{#snippet content()}
		{#if selectedLack}
			<header class="flex justify-between items-start">
				<div>
					<h2 class="h2">{selectedLack.lackType}</h2>
					<div class="flex gap-2 mt-2">
						<span class="badge {getStatusColor(selectedLack.status)} text-xs">
							{selectedLack.status.replace('_', ' ')}
						</span>
						<span class="badge {getPriorityColor(selectedLack.priority)} text-xs">
							{selectedLack.priority} priority
						</span>
					</div>
				</div>
				<button 
					class="btn-icon preset-tonal" 
					onclick={() => (showLackModal = false)}
				>
					<X size={16} />
				</button>
			</header>

			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<!-- Basic Information -->
				<div class="space-y-4">
					<h3 class="h3">Basic Information</h3>
					<div class="space-y-3">
						<div class="flex items-center gap-3">
							<Package size={18} class="opacity-60" />
							<div>
								<p class="text-sm opacity-60">Description</p>
								<p class="font-medium">{selectedLack.description}</p>
							</div>
						</div>

						<div class="flex items-center gap-3">
							<Building size={18} class="opacity-60" />
							<div>
								<p class="text-sm opacity-60">Department</p>
								<p class="font-medium">{selectedLack.department}</p>
							</div>
						</div>

						<div class="flex items-center gap-3">
							<Activity size={18} class="opacity-60" />
							<div>
								<p class="text-sm opacity-60">Production Line</p>
								<p class="font-medium">{selectedLack.productionLine}</p>
							</div>
						</div>

						<div class="flex items-center gap-3">
							<User size={18} class="opacity-60" />
							<div>
								<p class="text-sm opacity-60">Assigned To</p>
								<p class="font-medium">{selectedLack.assignedTo || 'Unassigned'}</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Progress & Metrics -->
				<div class="space-y-4">
					<h3 class="h3">Progress & Metrics</h3>
					<div class="space-y-4">
						<!-- Progress Bar -->
						<div>
							<div class="flex justify-between text-sm mb-2">
								<span>Items Progress</span>
								<span>{selectedLack.itemsProduced} / {selectedLack.totalItemsNeeded}</span>
							</div>
							<div class="w-full bg-surface-300-600 rounded-full h-4">
								<div 
									class="h-4 rounded-full transition-all duration-300 {getProgressColor((selectedLack.itemsProduced / selectedLack.totalItemsNeeded) * 100)}"
									style="width: {(selectedLack.itemsProduced / selectedLack.totalItemsNeeded) * 100}%"
								></div>
							</div>
							<p class="text-center text-sm opacity-60 mt-1">
								{Math.round((selectedLack.itemsProduced / selectedLack.totalItemsNeeded) * 100)}% Complete
							</p>
						</div>

						<!-- Metrics Grid -->
						<div class="grid grid-cols-1 gap-4">
							<div class="card p-4">
								<div class="flex items-center gap-2">
									<Clock size={16} class="text-primary-500" />
									<div>
										<p class="text-xs opacity-60">Estimated Hours</p>
										<p class="font-bold">{selectedLack.estimatedHours}h</p>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Timeline -->
			<div class="space-y-4">
				<h3 class="h3">Timeline</h3>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div class="flex items-center gap-3">
						<Calendar size={18} class="text-primary-500" />
						<div>
							<p class="text-sm opacity-60">Created Date</p>
							<p class="font-medium">{selectedLack.createdAt.toLocaleDateString()}</p>
						</div>
					</div>

					<div class="flex items-center gap-3">
						<Calendar size={18} class="text-warning-500" />
						<div>
							<p class="text-sm opacity-60">Target Completion</p>
							<p class="font-medium">{selectedLack.targetCompletionDate.toLocaleDateString()}</p>
							<p class="text-xs {getTimelineStatus(selectedLack.targetCompletionDate).color}">
								{getTimelineStatus(selectedLack.targetCompletionDate).text}
							</p>
						</div>
					</div>
				</div>
			</div>

			<!-- Items Breakdown -->
			<div class="space-y-4">
				<h3 class="h3">Items Breakdown</h3>
				<div class="grid grid-cols-3 gap-4">
					<div class="card p-4 text-center">
						<p class="text-2xl font-bold text-primary-500">{selectedLack.totalItemsNeeded}</p>
						<p class="text-sm opacity-60">Total Needed</p>
					</div>
					<div class="card p-4 text-center">
						<p class="text-2xl font-bold text-success-500">{selectedLack.itemsProduced}</p>
						<p class="text-sm opacity-60">Produced</p>
					</div>
					<div class="card p-4 text-center">
						<p class="text-2xl font-bold text-warning-500">{selectedLack.totalItemsNeeded - selectedLack.itemsProduced}</p>
						<p class="text-sm opacity-60">Remaining</p>
					</div>
				</div>
			</div>
		{/if}
	{/snippet}
</Modal> 