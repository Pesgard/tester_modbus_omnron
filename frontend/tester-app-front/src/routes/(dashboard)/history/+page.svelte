
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
	interface FailureCode {
		code: number; // 1-5
		name: string;
		description: string;
		count: number;
		percentage: number;
	}

	interface PieceModel {
		modelName: string;
		cameras: number; // 2 o 3 cámaras
		totalPieces: number;
		goodPieces: number;
		badPieces: number;
		failurePercentage: number;
		failures: FailureCode[];
	}

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
		// Nuevos campos para el sistema de fallas
		batchNumber: string;
		models: PieceModel[];
		totalGoodPieces: number;
		totalBadPieces: number;
		overallFailureRate: number;
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
			estimatedHours: 24,
			batchNumber: 'BATCH-001',
			models: [
				{
					modelName: 'Gear Model A',
					cameras: 2,
					totalPieces: 100,
					goodPieces: 95,
					badPieces: 5,
					failurePercentage: 5,
					failures: [
						{ code: 1, name: 'Alignment Error', description: 'Gear not aligned correctly', count: 2, percentage: 2 },
						{ code: 2, name: 'Surface Defect', description: 'Scratches on gear surface', count: 3, percentage: 3 }
					]
				},
				{
					modelName: 'Gear Model B',
					cameras: 3,
					totalPieces: 150,
					goodPieces: 140,
					badPieces: 10,
					failurePercentage: 6.67,
					failures: [
						{ code: 1, name: 'Alignment Error', description: 'Gear not aligned correctly', count: 3, percentage: 2 },
						{ code: 3, name: 'Material Defect', description: 'Cracks in gear material', count: 7, percentage: 4.67 }
					]
				}
			],
			totalGoodPieces: 100,
			totalBadPieces: 10,
			overallFailureRate: 10
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
			estimatedHours: 16,
			batchNumber: 'BATCH-002',
			models: [
				{
					modelName: 'Sensor Model X',
					cameras: 2,
					totalPieces: 80,
					goodPieces: 78,
					badPieces: 2,
					failurePercentage: 2.5,
					failures: [
						{ code: 1, name: 'Sensor Failure', description: 'Sensor not responding', count: 1, percentage: 1.25 },
						{ code: 4, name: 'Power Supply Issue', description: 'Power supply to sensor is unstable', count: 1, percentage: 1.25 }
					]
				},
				{
					modelName: 'Sensor Model Y',
					cameras: 3,
					totalPieces: 120,
					goodPieces: 115,
					badPieces: 5,
					failurePercentage: 4.17,
					failures: [
						{ code: 1, name: 'Sensor Failure', description: 'Sensor not responding', count: 2, percentage: 1.67 },
						{ code: 5, name: 'Physical Damage', description: 'Sensor damaged during transport', count: 3, percentage: 2.5 }
					]
				}
			],
			totalGoodPieces: 80,
			totalBadPieces: 5,
			overallFailureRate: 6.25
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
			estimatedHours: 8,
			batchNumber: 'BATCH-001',
			models: [
				{
					modelName: 'Calibrator Model 1',
					cameras: 2,
					totalPieces: 50,
					goodPieces: 48,
					badPieces: 2,
					failurePercentage: 4,
					failures: [
						{ code: 1, name: 'Calibration Error', description: 'Calibration data incorrect', count: 1, percentage: 2 }
					]
				}
			],
			totalGoodPieces: 48,
			totalBadPieces: 2,
			overallFailureRate: 4
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
			estimatedHours: 32,
			batchNumber: 'BATCH-003',
			models: [
				{
					modelName: 'PPE Model A',
					cameras: 2,
					totalPieces: 150,
					goodPieces: 145,
					badPieces: 5,
					failurePercentage: 3.33,
					failures: [
						{ code: 1, name: 'PPE Defect', description: 'PPE damaged during transport', count: 3, percentage: 2 },
						{ code: 2, name: 'Size Mismatch', description: 'PPE size does not match requirements', count: 2, percentage: 1.33 }
					]
				},
				{
					modelName: 'PPE Model B',
					cameras: 3,
					totalPieces: 200,
					goodPieces: 195,
					badPieces: 5,
					failurePercentage: 2.5,
					failures: [
						{ code: 1, name: 'PPE Defect', description: 'PPE damaged during transport', count: 2, percentage: 1 },
						{ code: 3, name: 'Size Mismatch', description: 'PPE size does not match requirements', count: 3, percentage: 1.5 }
					]
				}
			],
			totalGoodPieces: 145,
			totalBadPieces: 5,
			overallFailureRate: 3.33
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
			estimatedHours: 20,
			batchNumber: 'BATCH-002',
			models: [
				{
					modelName: 'Hydraulic Part 1',
					cameras: 2,
					totalPieces: 60,
					goodPieces: 58,
					badPieces: 2,
					failurePercentage: 3.33,
					failures: [
						{ code: 1, name: 'Hydraulic Leak', description: 'Hydraulic fluid leaking', count: 1, percentage: 1.67 },
						{ code: 4, name: 'Component Failure', description: 'Hydraulic component damaged', count: 1, percentage: 1.67 }
					]
				},
				{
					modelName: 'Hydraulic Part 2',
					cameras: 3,
					totalPieces: 90,
					goodPieces: 88,
					badPieces: 2,
					failurePercentage: 2.22,
					failures: [
						{ code: 1, name: 'Hydraulic Leak', description: 'Hydraulic fluid leaking', count: 1, percentage: 1.11 },
						{ code: 5, name: 'Component Failure', description: 'Hydraulic component damaged', count: 1, percentage: 1.11 }
					]
				}
			],
			totalGoodPieces: 58,
			totalBadPieces: 2,
			overallFailureRate: 3.33
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
			estimatedHours: 40,
			batchNumber: 'BATCH-001',
			models: [
				{
					modelName: 'Control Module 1',
					cameras: 2,
					totalPieces: 40,
					goodPieces: 38,
					badPieces: 2,
					failurePercentage: 5,
					failures: [
						{ code: 1, name: 'Control Error', description: 'Control module not responding', count: 1, percentage: 2.5 },
						{ code: 2, name: 'Power Supply Issue', description: 'Power supply to control module is unstable', count: 1, percentage: 2.5 }
					]
				},
				{
					modelName: 'Control Module 2',
					cameras: 3,
					totalPieces: 60,
					goodPieces: 58,
					badPieces: 2,
					failurePercentage: 3.33,
					failures: [
						{ code: 1, name: 'Control Error', description: 'Control module not responding', count: 1, percentage: 1.67 },
						{ code: 3, name: 'Power Supply Issue', description: 'Power supply to control module is unstable', count: 1, percentage: 1.67 }
					]
				}
			],
			totalGoodPieces: 38,
			totalBadPieces: 2,
			overallFailureRate: 5
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

	function viewLackDetails(lack: LackOrder) {
		selectedLack = lack;
		showLackModal = true;
	}

	function exportToCSV() {
		const headers = [
			'ID', 'Lack Type', 'Description', 'Batch Number', 'Status', 'Priority', 
			'Department', 'Production Line', 'Good Pieces', 'Bad Pieces', 
			'Failure Rate %', 'Models', 'Failure Codes', 'Created Date', 
			'Target Date', 'Assigned To', 'Estimated Hours'
		];

		const csvData = filteredLacks.map(lack => {
			const modelsInfo = lack.models.map(model => 
				`${model.modelName} (${model.cameras} cameras: ${model.goodPieces}/${model.totalPieces})`
			).join('; ');
			
			const failuresInfo = lack.models.map(model => 
				model.failures.map(failure => 
					`Code ${failure.code}: ${failure.name} (${failure.count} - ${failure.percentage.toFixed(1)}%)`
				).join(', ')
			).join('; ');

			return [
				lack.id,
				`"${lack.lackType.replace(/"/g, '""')}"`,
				`"${lack.description.replace(/"/g, '""')}"`,
				lack.batchNumber,
				lack.status,
				lack.priority,
				lack.department,
				lack.productionLine,
				lack.totalGoodPieces,
				lack.totalBadPieces,
				lack.overallFailureRate.toFixed(2),
				`"${modelsInfo.replace(/"/g, '""')}"`,
				`"${failuresInfo.replace(/"/g, '""')}"`,
				lack.createdAt.toISOString().split('T')[0],
				lack.targetCompletionDate.toISOString().split('T')[0],
				lack.assignedTo || 'Unassigned',
				lack.estimatedHours
			];
		});

		const csvContent = [headers, ...csvData]
			.map(row => row.join(','))
			.join('\n');

		const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
		const link = document.createElement('a');
		const url = URL.createObjectURL(blob);
		link.setAttribute('href', url);
		link.setAttribute('download', `batch_failure_report_${new Date().toISOString().split('T')[0]}.csv`);
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

<div class="flex flex-col h-full">
	<!-- App Bar -->


	<!-- Main Dashboard -->
	<div class="flex-1 p-6 space-y-6 overflow-auto">
		<!-- Summary Cards -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
			<!-- Total Batches -->
			<div class="card p-6 space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="h3">Total Batches</h3>
					<Package size={24} class="text-primary-500" />
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

			<!-- Good Pieces -->
			<div class="card p-6 space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="h3">Good Pieces</h3>
					<TrendingUp size={24} class="text-success-500" />
				</div>
				<div>
					<p class="text-3xl font-bold text-success-500">{lacks.reduce((sum, l) => sum + l.totalGoodPieces, 0)}</p>
					<p class="text-sm opacity-75">of {lacks.reduce((sum, l) => sum + l.totalGoodPieces + l.totalBadPieces, 0)} total pieces</p>
					<div class="w-full bg-surface-300-600 rounded-full h-3 mt-2">
						<div 
							class="h-3 rounded-full bg-success-500 transition-all duration-300"
							style="width: {((lacks.reduce((sum, l) => sum + l.totalGoodPieces, 0) / lacks.reduce((sum, l) => sum + l.totalGoodPieces + l.totalBadPieces, 0)) * 100)}%"
						></div>
					</div>
					<p class="text-sm opacity-60 mt-1">{((lacks.reduce((sum, l) => sum + l.totalGoodPieces, 0) / lacks.reduce((sum, l) => sum + l.totalGoodPieces + l.totalBadPieces, 0)) * 100).toFixed(1)}% Quality</p>
				</div>
			</div>

			<!-- Failed Pieces -->
			<div class="card p-6 space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="h3">Failed Pieces</h3>
					<AlertTriangle size={24} class="text-error-500" />
				</div>
				<div>
					<p class="text-3xl font-bold text-error-500">{lacks.reduce((sum, l) => sum + l.totalBadPieces, 0)}</p>
					<p class="text-sm opacity-75">Average rate: {(lacks.reduce((sum, l) => sum + l.overallFailureRate, 0) / lacks.length).toFixed(1)}%</p>
					<div class="w-full bg-surface-300-600 rounded-full h-3 mt-2">
						<div 
							class="h-3 rounded-full bg-error-500 transition-all duration-300"
							style="width: {(lacks.reduce((sum, l) => sum + l.overallFailureRate, 0) / lacks.length)}%"
						></div>
					</div>
					<p class="text-sm opacity-60 mt-1">Requires attention</p>
				</div>
			</div>

			<!-- Active Models -->
			<div class="card p-6 space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="h3">Active Models</h3>
					<Activity size={24} class="text-primary-500" />
				</div>
				<div>
					<p class="text-3xl font-bold">{lacks.reduce((sum, l) => sum + l.models.length, 0)}</p>
					<div class="flex gap-2 text-sm mt-2">
						<span class="badge preset-filled-primary-500 text-xs">
							{lacks.reduce((sum, l) => sum + l.models.filter(m => m.cameras === 2).length, 0)} with 2 cameras
						</span>
						<span class="badge preset-filled-secondary-500 text-xs">
							{lacks.reduce((sum, l) => sum + l.models.filter(m => m.cameras === 3).length, 0)} with 3 cameras
						</span>
					</div>
					<p class="text-sm opacity-60 mt-1">In production</p>
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
							<th>Batch & Details</th>
							<th>Models & Cameras</th>
							<th>Good/Bad Pieces</th>
							<th>Failure Rate</th>
							<th>Status</th>
							<th>Priority</th>
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
										<p class="text-xs font-medium text-primary-500">Batch: {lack.batchNumber}</p>
										<p class="text-xs opacity-50">Line: {lack.productionLine}</p>
									</div>
								</td>
								<td>
									<div class="space-y-1">
										{#each lack.models as model}
											<div class="text-xs bg-surface-200-700 rounded px-2 py-1">
												<p class="font-medium">{model.modelName}</p>
												<p class="opacity-60">{model.cameras} cameras • {model.totalPieces} pieces</p>
											</div>
										{/each}
									</div>
								</td>
								<td>
									<div class="space-y-2">
										<div class="flex justify-between text-xs">
											<span class="text-success-500">Good: {lack.totalGoodPieces}</span>
											<span class="text-error-500">Bad: {lack.totalBadPieces}</span>
										</div>
										<div class="w-full bg-surface-300-600 rounded-full h-2">
											<div 
												class="h-2 rounded-full bg-success-500 transition-all duration-300"
												style="width: {((lack.totalGoodPieces / (lack.totalGoodPieces + lack.totalBadPieces)) * 100)}%"
											></div>
										</div>
										<p class="text-xs opacity-60 text-center">
											{Math.round((lack.totalGoodPieces / (lack.totalGoodPieces + lack.totalBadPieces)) * 100)}% good
										</p>
									</div>
								</td>
								<td>
									<div class="text-center">
										<p class="text-lg font-bold {lack.overallFailureRate > 5 ? 'text-error-500' : lack.overallFailureRate > 2 ? 'text-warning-500' : 'text-success-500'}">
											{lack.overallFailureRate.toFixed(1)}%
										</p>
										<p class="text-xs opacity-60">failures</p>
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
										<p class="text-sm font-medium {getTimelineStatus(lack.targetCompletionDate).color}">
											{getTimelineStatus(lack.targetCompletionDate).text}
										</p>
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

			<!-- Batch Information -->
			<div class="card p-4 bg-primary-500/10 border-l-4 border-primary-500">
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div>
						<p class="text-sm opacity-60">Batch Number</p>
						<p class="font-bold text-lg">{selectedLack.batchNumber}</p>
					</div>
					<div>
						<p class="text-sm opacity-60">Department</p>
						<p class="font-medium">{selectedLack.department}</p>
					</div>
					<div>
						<p class="text-sm opacity-60">Production Line</p>
						<p class="font-medium">{selectedLack.productionLine}</p>
					</div>
				</div>
			</div>

			<!-- General Failure Summary -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
				<div class="card p-4 text-center">
					<p class="text-2xl font-bold text-success-500">{selectedLack.totalGoodPieces}</p>
					<p class="text-sm opacity-60">Good Pieces</p>
				</div>
				<div class="card p-4 text-center">
					<p class="text-2xl font-bold text-error-500">{selectedLack.totalBadPieces}</p>
					<p class="text-sm opacity-60">Bad Pieces</p>
				</div>
				<div class="card p-4 text-center">
					<p class="text-2xl font-bold {selectedLack.overallFailureRate > 5 ? 'text-error-500' : selectedLack.overallFailureRate > 2 ? 'text-warning-500' : 'text-success-500'}">
						{selectedLack.overallFailureRate.toFixed(1)}%
					</p>
					<p class="text-sm opacity-60">Failure Rate</p>
				</div>
				<div class="card p-4 text-center">
					<p class="text-2xl font-bold text-primary-500">{selectedLack.models.length}</p>
					<p class="text-sm opacity-60">Models</p>
				</div>
			</div>

			<!-- Model Details -->
			<div class="space-y-4">
				<h3 class="h3">Model Details</h3>
				<div class="grid gap-4">
					{#each selectedLack.models as model}
						<div class="card p-6 space-y-4">
							<div class="flex justify-between items-start">
								<div>
									<h4 class="h4">{model.modelName}</h4>
									<p class="text-sm opacity-60">{model.cameras} inspection cameras</p>
								</div>
								<div class="text-right">
									<p class="text-lg font-bold {model.failurePercentage > 5 ? 'text-error-500' : model.failurePercentage > 2 ? 'text-warning-500' : 'text-success-500'}">
										{model.failurePercentage.toFixed(1)}%
									</p>
									<p class="text-xs opacity-60">failures</p>
								</div>
							</div>

							<!-- Model Progress -->
							<div>
								<div class="flex justify-between text-sm mb-2">
									<span class="text-success-500">Good: {model.goodPieces}</span>
									<span class="text-error-500">Bad: {model.badPieces}</span>
									<span class="opacity-60">Total: {model.totalPieces}</span>
								</div>
								<div class="w-full bg-surface-300-600 rounded-full h-3">
									<div 
										class="h-3 rounded-full bg-success-500 transition-all duration-300"
										style="width: {(model.goodPieces / model.totalPieces) * 100}%"
									></div>
								</div>
							</div>

							<!-- Failure Codes -->
							{#if model.failures.length > 0}
								<div class="space-y-2">
									<h5 class="font-semibold text-sm">Failure Codes</h5>
									<div class="grid gap-2">
										{#each model.failures as failure}
											<div class="bg-surface-200-700 rounded p-3 flex justify-between items-center">
												<div class="flex items-center gap-3">
													<span class="badge preset-filled-error-500 text-xs font-bold">
														{failure.code}
													</span>
													<div>
														<p class="font-medium text-sm">{failure.name}</p>
														<p class="text-xs opacity-60">{failure.description}</p>
													</div>
												</div>
												<div class="text-right">
													<p class="font-bold">{failure.count}</p>
													<p class="text-xs opacity-60">{failure.percentage.toFixed(1)}%</p>
												</div>
											</div>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					{/each}
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
							<p class="text-sm opacity-60">Target Date</p>
							<p class="font-medium">{selectedLack.targetCompletionDate.toLocaleDateString()}</p>
							<p class="text-xs {getTimelineStatus(selectedLack.targetCompletionDate).color}">
								{getTimelineStatus(selectedLack.targetCompletionDate).text}
							</p>
						</div>
					</div>
				</div>
			</div>

			<!-- Additional Information -->
			<div class="space-y-4">
				<h3 class="h3">Additional Information</h3>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div class="card p-4">
						<div class="flex items-center gap-3">
							<User size={18} class="text-primary-500" />
							<div>
								<p class="text-sm opacity-60">Assigned To</p>
								<p class="font-medium">{selectedLack.assignedTo || 'Unassigned'}</p>
							</div>
						</div>
					</div>
					<div class="card p-4">
						<div class="flex items-center gap-3">
							<Clock size={18} class="text-primary-500" />
							<div>
								<p class="text-sm opacity-60">Estimated Hours</p>
								<p class="font-medium">{selectedLack.estimatedHours}h</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		{/if}
	{/snippet}
</Modal> 