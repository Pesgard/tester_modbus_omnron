<script lang="ts">
	import type { PageData } from './$types';
	import { format } from 'date-fns';
	import { es } from 'date-fns/locale';
	import IconDownload from '@lucide/svelte/icons/download';
	import IconArrowLeft from '@lucide/svelte/icons/arrow-left';
	import IconCheckCircle from '@lucide/svelte/icons/check-circle';
	import IconXCircle from '@lucide/svelte/icons/x-circle';
	import IconImage from '@lucide/svelte/icons/image';
	import IconX from '@lucide/svelte/icons/x';
	import IconClock from '@lucide/svelte/icons/clock';
	import IconUser from '@lucide/svelte/icons/user';
	import IconPackage from '@lucide/svelte/icons/package';

	let { data }: { data: PageData } = $props();

	// console.log(data);

	const canExport = $derived(
		data.user?.permisos.includes('*') ||
			data.user?.permisos.includes('history.*') ||
			data.user?.permisos.includes('history.lotes.exportar')
	);

	// Image modal state
	let selectedImage = $state<{ path: string; tipo_falla: string; uploaded_at: Date } | null>(null);

	function openImageModal(image: { path: string; tipo_falla: string; uploaded_at: Date }) {
		selectedImage = image;
	}

	function closeImageModal() {
		selectedImage = null;
	}

	/**
	 * Export lot data to CSV
	 */
	function exportLotToCSV() {
		const { lote, stats } = data;
		
		// Prepare CSV content
		const csvLines: string[] = [];
		
		// Header information
		csvLines.push('REPORTE DE LOTE');
		csvLines.push('');
		csvLines.push('INFORMACIÓN GENERAL');
		csvLines.push(`Nombre del Lote,${lote.name}`);
		csvLines.push(`PPN,${lote.receta.ppn}`);
		csvLines.push(`Descripción,${lote.receta.item_description}`);
		csvLines.push(`Estado,${lote.estado}`);
		csvLines.push(`Creado por,${lote.creator.username}`);
		csvLines.push(`Fecha de inicio,${format(new Date(lote.started_at), 'dd/MM/yyyy HH:mm', { locale: es })}`);
		if (lote.closed_at) {
			csvLines.push(`Fecha de cierre,${format(new Date(lote.closed_at), 'dd/MM/yyyy HH:mm', { locale: es })}`);
		}
		csvLines.push('');
		
		// Statistics
		csvLines.push('ESTADÍSTICAS');
		csvLines.push(`Total de piezas,${stats.total}`);
		csvLines.push(`Piezas OK,${lote.piezas_ok}`);
		csvLines.push(`Piezas NOK,${lote.piezas_fallas}`);
		csvLines.push(`Precisión,${stats.accuracy.toFixed(2)}%`);
		csvLines.push(`Tasa de defectos,${stats.defectRate.toFixed(2)}%`);
		csvLines.push('');
		
		// Failures by type
		if (Object.keys(stats.failuresByType).length > 0) {
			csvLines.push('FALLAS POR TIPO');
			Object.entries(stats.failuresByType).forEach(([type, count]) => {
				csvLines.push(`${type},${count}`);
			});
			csvLines.push('');
		}
		
		// Pieces detail
		csvLines.push('DETALLE DE PIEZAS');
		csvLines.push('Índice,Estado,Fecha de procesamiento,Tiene imagen');
		lote.piezas.forEach((pieza) => {
			const estado = pieza.ok ? 'OK' : 'NOK';
			const fecha = pieza.processed_at
				? format(new Date(pieza.processed_at), 'dd/MM/yyyy HH:mm', { locale: es })
				: '';
			const tieneImagen = pieza.imagen_path ? 'Sí' : 'No';
			csvLines.push(`${pieza.indice},${estado},${fecha},${tieneImagen}`);
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
		link.setAttribute('download', `lote_${lote.name}_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`);
		link.style.visibility = 'hidden';
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}
</script>

<div class="lot-details-page p-6 h-full overflow-auto">
	<!-- Header -->
	<div class="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
		<div class="w-full md:w-auto">
			<div class="flex items-center gap-3 mb-2 flex-wrap">
				<a href="/dashboard/history" class="btn variant-ghost-surface touch-manipulation">
					<IconArrowLeft size={20} />
					<span>Back to History</span>
				</a>
				<span
					class="badge text-sm px-3 py-1"
					class:variant-filled-success={data.lote.estado === 'CLOSED'}
					class:variant-filled-warning={data.lote.estado === 'PAUSED'}
				>
					{data.lote.estado}
				</span>
			</div>
			<h1 class="text-3xl font-bold">{data.lote.name}</h1>
			<p class="text-surface-600-400 mt-1">
				{data.lote.receta.ppn} - {data.lote.receta.item_description}
			</p>
		</div>

		{#if canExport}
			<button class="btn variant-filled-primary touch-manipulation text-base px-6 py-3 min-h-[56px] w-full md:w-auto" onclick={exportLotToCSV}>
				<IconDownload size={20} />
				<span>Export to CSV</span>
			</button>
		{/if}
	</div>

	<!-- Statistics Grid -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
		<div class="card variant-filled-success/10 p-4">
			<div class="flex items-center gap-2 text-sm text-surface-600-400 mb-2">
				<IconCheckCircle size={16} />
				<span>OK Pieces</span>
			</div>
			<div class="text-3xl font-bold text-success-500">{data.lote.piezas_ok}</div>
			<div class="text-xs text-surface-600-400 mt-1">
				{data.stats.accuracy.toFixed(1)}% accuracy
			</div>
		</div>

		<div class="card variant-filled-error/10 p-4">
			<div class="flex items-center gap-2 text-sm text-surface-600-400 mb-2">
				<IconXCircle size={16} />
				<span>NOK Pieces</span>
			</div>
			<div class="text-3xl font-bold text-error-500">{data.lote.piezas_fallas}</div>
			<div class="text-xs text-surface-600-400 mt-1">
				{data.stats.defectRate.toFixed(1)}% defect rate
			</div>
		</div>

		<div class="card variant-glass-surface p-4">
			<div class="flex items-center gap-2 text-sm text-surface-600-400 mb-2">
				<IconPackage size={16} />
				<span>Total Pieces</span>
			</div>
			<div class="text-3xl font-bold">{data.stats.total}</div>
			<div class="text-xs text-surface-600-400 mt-1">
				Target: {data.lote.max_piezas_ok}
			</div>
		</div>

		<div class="card variant-glass-surface p-4">
			<div class="flex items-center gap-2 text-sm text-surface-600-400 mb-2">
				<IconImage size={16} />
				<span>Images Captured</span>
			</div>
			<div class="text-3xl font-bold">{data.lote.imagenes.length}</div>
			<div class="text-xs text-surface-600-400 mt-1">
				Defect images
			</div>
		</div>
	</div>

	<!-- Lot Information -->
	<div class="card variant-glass-surface p-6 mb-6">
		<h2 class="h3 mb-4">Lot Information</h2>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<div class="flex items-start gap-3">
				<IconUser size={20} class="text-surface-600-400 mt-1" />
				<div>
					<p class="text-sm text-surface-600-400">Created by</p>
					<p class="font-semibold">{data.lote.creator.username}</p>
				</div>
			</div>
			<div class="flex items-start gap-3">
				<IconPackage size={20} class="text-surface-600-400 mt-1" />
				<div>
					<p class="text-sm text-surface-600-400">Recipe</p>
					<p class="font-semibold">{data.lote.receta.ppn}</p>
				</div>
			</div>
			<div class="flex items-start gap-3">
				<IconClock size={20} class="text-surface-600-400 mt-1" />
				<div>
					<p class="text-sm text-surface-600-400">Started at</p>
					<p class="font-semibold">
						{format(new Date(data.lote.started_at), 'PPpp', { locale: es })}
					</p>
				</div>
			</div>
			{#if data.lote.closed_at}
				<div class="flex items-start gap-3">
					<IconClock size={20} class="text-surface-600-400 mt-1" />
					<div>
						<p class="text-sm text-surface-600-400">Closed at</p>
						<p class="font-semibold">
							{format(data.lote.closed_at, 'PPpp', { locale: es })}
						</p>
					</div>
				</div>
			{/if}
		</div>
	</div>

	<!-- Failures by Type -->
	{#if Object.keys(data.stats.failuresByType).length > 0}
		<div class="card variant-glass-surface p-6 mb-6">
			<h2 class="h3 mb-4">Failures by Type</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each Object.entries(data.stats.failuresByType) as [type, count]}
					<div class="flex items-center justify-between p-3 card variant-ghost-error">
						<span class="font-medium">{type}</span>
						<span class="badge variant-filled-error">{count}</span>
					</div>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Images Gallery -->
	{#if data.lote.imagenes.length > 0}
		<div class="card variant-glass-surface p-6 mb-6">
			<h2 class="h3 mb-4">Defect Images ({data.lote.imagenes.length})</h2>
			<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
				{#each data.lote.imagenes as imagen}
					<button
						class="card variant-ghost-surface overflow-hidden hover:variant-soft-primary transition-all touch-manipulation"
						onclick={() => openImageModal(imagen)}
					>
						<img src={imagen.path} alt={imagen.tipo_falla} class="w-full h-48 object-cover" />
						<div class="p-3">
							<p class="text-sm font-semibold truncate flex items-center gap-2">
								<IconImage size={14} />
								{imagen.tipo_falla}
							</p>
							<p class="text-xs text-surface-600-400 flex items-center gap-1 mt-1">
								<IconClock size={12} />
								{format(imagen.uploaded_at, 'dd/MM/yyyy HH:mm', { locale: es })}
							</p>
						</div>
					</button>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Pieces Table -->
	<div class="card variant-glass-surface p-6 mb-6">
		<h2 class="h3 mb-4">All Pieces ({data.lote.piezas.length})</h2>
		<div class="table-container">
			<table class="table table-hover">
				<thead>
					<tr>
						<th>Index</th>
						<th>Status</th>
						<th>Processed At</th>
						<th>Has Image</th>
					</tr>
				</thead>
				<tbody>
					{#each data.lote.piezas as pieza}
						<tr>
							<td class="font-mono">#{pieza.indice}</td>
							<td>
								<span
									class="badge flex items-center gap-1 w-fit"
									class:variant-filled-success={pieza.ok}
									class:variant-filled-error={!pieza.ok}
								>
									{#if pieza.ok}
										<IconCheckCircle size={14} />
										<span>OK</span>
									{:else}
										<IconXCircle size={14} />
										<span>NOK</span>
									{/if}
								</span>
							</td>
							<td class="text-sm">
								{#if pieza.processed_at}
									{format(pieza.processed_at, 'dd/MM/yyyy HH:mm', { locale: es })}
								{:else}
									<span class="text-surface-600-400">—</span>
								{/if}
							</td>
							<td>
								{#if pieza.imagen_path}
									<span class="badge variant-soft-success flex items-center gap-1 w-fit">
										<IconImage size={14} />
										<span>Yes</span>
									</span>
								{:else}
									<span class="text-surface-600-400">—</span>
								{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>

<!-- Image Modal -->
{#if selectedImage}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm p-4"
		onclick={closeImageModal}
	>
		<div class="max-w-4xl w-full" onclick={(e) => e.stopPropagation()}>
			<div class="flex items-center justify-between mb-4">
				<div class="text-white">
					<h3 class="text-2xl font-bold flex items-center gap-2">
						<IconImage size={28} />
						{selectedImage.tipo_falla}
					</h3>
					<p class="text-base opacity-90 mt-2 flex items-center gap-2">
						<IconClock size={16} />
						{format(selectedImage.uploaded_at, 'PPpp', { locale: es })}
					</p>
				</div>
				<button 
					class="btn-icon variant-filled w-12 h-12 touch-manipulation" 
					onclick={closeImageModal} 
					aria-label="Close"
				>
					<IconX size={28} />
				</button>
			</div>
			<img
				src={selectedImage.path}
				alt={selectedImage.tipo_falla}
				class="w-full h-auto rounded-lg"
			/>
		</div>
	</div>
{/if}

<style>
	.badge {
		padding: 0.25rem 0.75rem;
		border-radius: 9999px;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
	}

	/* Enhanced touch targets */
	.touch-manipulation {
		-webkit-tap-highlight-color: transparent;
		touch-action: manipulation;
	}
</style>

