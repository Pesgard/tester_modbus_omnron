<script lang="ts">
	import type { PageData } from './$types';
	import { format } from 'date-fns';
	import { es } from 'date-fns/locale';
	import IconDownload from '@lucide/svelte/icons/download';
	import IconBarChart from '@lucide/svelte/icons/bar-chart';

	let { data }: { data: PageData } = $props();

	let searchQuery = $state('');
	let statusFilter = $state<'all' | 'CLOSED' | 'PAUSED'>('all');

	const filteredLotes = $derived.by(() => {
		let filtered = data.lotes;

		// Apply search filter
		if (searchQuery) {
			filtered = filtered.filter(
				(lote) =>
					lote.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
					lote.receta.ppn.toLowerCase().includes(searchQuery.toLowerCase())
			);
		}

		// Apply status filter
		if (statusFilter !== 'all') {
			filtered = filtered.filter((lote) => lote.estado === statusFilter);
		}

		return filtered;
	});

	const canExport = $derived(
		data.user?.permisos.includes('*') ||
			data.user?.permisos.includes('history.*') ||
			data.user?.permisos.includes('history.lotes.exportar')
	);

	/**
	 * Export all lots to CSV
	 */
	function exportAllLotesToCSV() {
		const csvLines: string[] = [];
		
		// Header
		csvLines.push('REPORTE DE TODOS LOS LOTES');
		csvLines.push(`Fecha de generación,${format(new Date(), 'dd/MM/yyyy HH:mm', { locale: es })}`);
		csvLines.push('');
		csvLines.push('Nombre del Lote,PPN,Descripción,Estado,Piezas OK,Piezas NOK,Total,Precisión %,Creado por,Fecha de inicio,Fecha de cierre');
		
		// Data rows
		filteredLotes.forEach((lote) => {
			const total = lote.piezas_ok + lote.piezas_fallas;
			const accuracy = total > 0 ? ((lote.piezas_ok / total) * 100).toFixed(2) : '0';
			const startDate = format(new Date(lote.started_at), 'dd/MM/yyyy HH:mm', { locale: es });
			const closedDate = lote.closed_at 
				? format(new Date(lote.closed_at), 'dd/MM/yyyy HH:mm', { locale: es })
				: '—';
			
			csvLines.push(
				`${lote.name},${lote.receta.ppn},"${lote.receta.item_description}",${lote.estado},${lote.piezas_ok},${lote.piezas_fallas},${total},${accuracy},${lote.creator.username},${startDate},${closedDate}`
			);
		});
		
		// Join all lines
		const csvContent = csvLines.join('\n');
		
		// Add BOM for proper UTF-8 encoding in Excel
		const BOM = '\uFEFF';
		const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
		
		// Create download link
		const link = document.createElement('a');
		const url = URL.createObjectURL(blob);
		link.setAttribute('href', url);
		link.setAttribute('download', `lotes_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`);
		link.style.visibility = 'hidden';
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}
</script>

<div class="history-page p-6 h-full overflow-auto">
	<h1 class="text-3xl font-bold mb-6">History - Completed Lots</h1>

	<!-- Filters -->
	<div class="card p-4 mb-6">
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<div>
				<label for="search" class="block text-sm font-medium mb-2">Search</label>
				<input
					id="search"
					type="text"
					class="input"
					placeholder="Lot name or PPN..."
					bind:value={searchQuery}
				/>
			</div>

			<div>
				<label for="status" class="block text-sm font-medium mb-2">Status</label>
				<select id="status" class="select" bind:value={statusFilter}>
					<option value="all">All</option>
					<option value="CLOSED">Closed</option>
					<option value="PAUSED">Paused</option>
				</select>
			</div>

			{#if canExport}
				<div class="flex items-end">
					<button class="btn variant-filled-primary touch-manipulation text-base px-6 py-3 min-h-[56px]" onclick={exportAllLotesToCSV}>
						<IconDownload size={20} />
						<span>Export All to CSV</span>
					</button>
				</div>
			{/if}
		</div>
	</div>

	<!-- Lots Table -->
	<div class="card p-6">
		<h2 class="text-xl font-semibold mb-4">
			Lots ({filteredLotes.length})
		</h2>

		<div class="overflow-x-auto">
			<table class="table w-full">
				<thead>
					<tr>
						<th>Lot Name</th>
						<th>Recipe (PPN)</th>
						<th>Status</th>
						<th>OK</th>
						<th>NOK</th>
						<th>Total</th>
						<th>Accuracy</th>
						<th>Created By</th>
						<th>Completed</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each filteredLotes as lote}
						{@const total = lote.piezas_ok + lote.piezas_fallas}
						{@const accuracy = total > 0 ? (lote.piezas_ok / total) * 100 : 0}
						<tr>
							<td class="font-semibold">{lote.name}</td>
							<td>
								<div class="text-sm">{lote.receta.ppn}</div>
								<div class="text-xs text-surface-600-400">
									{lote.receta.item_description.slice(0, 50)}...
								</div>
							</td>
							<td>
								<span class="badge" class:badge-success={lote.estado === 'CLOSED'}>
									{lote.estado}
								</span>
							</td>
							<td class="text-success-500 font-semibold">{lote.piezas_ok}</td>
							<td class="text-error-500 font-semibold">{lote.piezas_fallas}</td>
							<td>{total}</td>
							<td>
								<span class:text-success-500={accuracy >= 95} class:text-warning-500={accuracy < 95 && accuracy >= 90} class:text-error-500={accuracy < 90}>
									{accuracy.toFixed(1)}%
								</span>
							</td>
							<td>{lote.creator.username}</td>
							<td>
								{#if lote.closed_at}
									{new Date(lote.closed_at).toLocaleDateString()}
								{:else}
									-
								{/if}
							</td>
							<td>
								<a href="/dashboard/history/{lote.id}" class="btn btn-sm variant-filled-primary touch-manipulation">
									<IconBarChart size={16} />
									<span>View Details</span>
								</a>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>

			{#if filteredLotes.length === 0}
				<div class="text-center py-8 text-surface-600-400">
					No lots found matching your filters.
				</div>
			{/if}
		</div>
	</div>
</div>

<style>
	.badge {
		padding: 0.25rem 0.75rem;
		border-radius: 9999px;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
	}

	.badge-success {
		background-color: rgba(34, 197, 94, 0.2);
		color: rgb(34, 197, 94);
	}

	/* Enhanced touch targets */
	.touch-manipulation {
		-webkit-tap-highlight-color: transparent;
		touch-action: manipulation;
	}
</style>

