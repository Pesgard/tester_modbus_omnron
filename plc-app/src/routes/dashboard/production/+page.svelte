<script lang="ts">
	import type { PageData } from './$types';
	import IconAlertTriangle from '@lucide/svelte/icons/alert-triangle';
	import IconX from '@lucide/svelte/icons/x';
	import IconAlertCircle from '@lucide/svelte/icons/alert-circle';
	import IconCheckCircle from '@lucide/svelte/icons/check-circle';
	import IconPause from '@lucide/svelte/icons/pause';
	import IconPlay from '@lucide/svelte/icons/play';
	import IconSquare from '@lucide/svelte/icons/square';

	let { data }: { data: PageData } = $props();

	// WebSocket connection
	let ws: WebSocket | null = $state(null);
	let plcData = $state<any>(null);
	let lineStatus = $state(data.lineStatus);
	let recentPieces = $state(data.recentPieces);
	let availableLotes = $state(data.availableLotes);

	// Error modal state
	let errorModal = $state<{
		show: boolean;
		message: string;
		imagePath: string | null;
		failureCode: number;
		piezaIndex: number;
		loteName: string;
	}>({
		show: false,
		message: '',
		imagePath: null,
		failureCode: 0,
		piezaIndex: 0,
		loteName: ''
	});

	// Stop production confirmation modal
	let stopProductionModal = $state<{
		show: boolean;
	}>({
		show: false
	});

	// Permission checks
	const canControl = $derived(
		data.user?.permisos.includes('*') ||
			data.user?.permisos.includes('production.*') ||
			data.user?.permisos.includes('production.control.start') ||
			data.user?.permisos.includes('production.control.stop')
	);

	const canViewMetrics = $derived(
		data.user?.permisos.includes('*') ||
			data.user?.permisos.includes('production.*') ||
			data.user?.permisos.includes('production.metrics.ver')
	);

	// Calculate metrics
	const metrics = $derived.by(() => {
		if (!lineStatus || lineStatus.status !== 'active' || !lineStatus.lote) {
			return {
				rate: 0,
				efficiency: 0,
				accuracy: 0,
				total: 0,
				ok: 0,
				nok: 0
			};
		}

		const lote = lineStatus.lote;
		const total = lote.piezasOk + lote.piezasFallas;
		const accuracy = total > 0 ? (lote.piezasOk / total) * 100 : 0;
		const efficiency = lote.maxPiezasOk > 0 ? (lote.piezasOk / lote.maxPiezasOk) * 100 : 0;

		return {
			rate: 0, // TODO: Calculate based on time
			efficiency,
			accuracy,
			total,
			ok: lote.piezasOk,
			nok: lote.piezasFallas
		};
	});

	// WebSocket connection using $effect (Svelte 5)
	$effect(() => {
		console.log('🔌 [Production] Initializing WebSocket connection...');
		
		// Create WebSocket connection to port 4000 (WebSocket server)
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const hostname = window.location.hostname;
		const socket = new WebSocket(`${protocol}//${hostname}:4000`);

		socket.onopen = () => {
			console.log('✅ [Production] WebSocket connected successfully');
			ws = socket;
		};

		socket.onmessage = (event) => {
			try {
				const message = JSON.parse(event.data);
				console.log('📨 [WS] Message received:', message.type, message.payload);

				switch (message.type) {
					case 'plc-data':
						plcData = message.payload;
						// console.log('📊 [WS] PLC Data updated:', plcData);
						break;

					case 'piece-created':
						console.log('✅ [WS] Piece created:', message.payload);
						
						// Create piece object from payload
						const newPiece = {
							id: message.payload.piezaId,
							lote_id: message.payload.loteId,
							indice: message.payload.index,
							ok: message.payload.ok,
							imagen_path: message.payload.hasImage ? 'pending' : '',
							processed_at: new Date().toISOString(),
							resultado_bits: message.payload.parsed?.rawData || [],
							isNew: true
						};
						
						// Add new piece to the top of the list
						recentPieces = [newPiece, ...recentPieces.slice(0, 19)];
						console.log('📝 [WS] Recent pieces updated, count:', recentPieces.length);
						
						// Remove isNew flag after animation (2 seconds)
						setTimeout(() => {
							const index = recentPieces.findIndex(p => p.id === newPiece.id);
							if (index !== -1) {
								const updated = [...recentPieces];
								updated[index] = { ...updated[index], isNew: false };
								recentPieces = updated;
								console.log('🎨 [WS] Removed isNew flag from piece', newPiece.id);
							}
						}, 2000);
						
						// Update line status counters in real-time
						if (lineStatus.lote) {
							const updatedLote = { ...lineStatus.lote };
							
							if (message.payload.ok) {
								updatedLote.piezasOk += 1;
							} else {
								updatedLote.piezasFallas += 1;
							}
							
							// Recalculate progress
							const total = updatedLote.piezasOk + updatedLote.piezasFallas;
							updatedLote.progress = updatedLote.maxPiezasOk > 0 
								? (updatedLote.piezasOk / updatedLote.maxPiezasOk) * 100 
								: 0;
							
							// Force reactive update by creating new object
							lineStatus = { ...lineStatus, lote: updatedLote };
							console.log('📊 [WS] Line status updated:', updatedLote);
						}
						break;

					case 'awaiting-image':
						console.log('📸 [WS] Awaiting image for piece:', message.payload.piezaIndex);
						// Mark piece as waiting for image
						const waitingIndex = recentPieces.findIndex(
							p => p.indice === message.payload.piezaIndex && p.lote_id === message.payload.loteId
						);
						if (waitingIndex !== -1) {
							const updated = [...recentPieces];
							updated[waitingIndex] = { ...updated[waitingIndex], imagen_path: 'pending' };
							recentPieces = updated;
						}
						break;

					case 'image-processed':
						console.log('🖼️ [WS] Image processed:', message.payload);
						
						// Update the piece with the image path
						const imageIndex = recentPieces.findIndex(
							p => p.indice === message.payload.piezaIndex && p.lote_id === message.payload.loteId
						);
						
						if (imageIndex !== -1) {
							const updated = [...recentPieces];
							updated[imageIndex] = { ...updated[imageIndex], imagen_path: message.payload.imagePath };
							recentPieces = updated;
							console.log('✅ [WS] Updated piece with image path:', message.payload.imagePath);
						}

						// 🛑 PAUSE PRODUCTION IMMEDIATELY to prevent cascading errors
						console.warn('⚠️ [WS] Pausing production due to failure detection');
						stopProductionDueToError();

						// Show error modal with the image
						errorModal = {
							show: true,
							message: `Falla detectada en pieza #${message.payload.piezaIndex}`,
							imagePath: message.payload.imagePath,
							failureCode: message.payload.failureCode || 0,
							piezaIndex: message.payload.piezaIndex,
							loteName: message.payload.loteName || ''
						};
						break;

					case 'lot-started':
						console.log('🚀 [WS] Lot started:', message.payload);
						// Clear recent pieces immediately
						recentPieces = [];
						// Then fetch full status
						fetchLineStatus();
						fetchAvailableLotes();
						break;

					case 'lot-stopped':
						console.log('⏹️ [WS] Lot stopped');
						// Clear recent pieces immediately
						recentPieces = [];
						// Then fetch full status
						fetchLineStatus();
						fetchAvailableLotes();
						break;

					case 'lot-completed':
						console.log('✅ [WS] Lot completed:', message.payload);
						// Update status
						fetchLineStatus();
						fetchAvailableLotes();
						break;

					case 'plc-error':
						console.error('❌ [WS] PLC Error:', message.payload);
						break;
						
					case 'image-error':
						console.error('❌ [WS] Image Error:', message.payload);
						break;
				}
			} catch (error) {
				console.error('❌ [WS] Error parsing message:', error);
			}
		};

		socket.onerror = (error) => {
			console.error('❌ [WS] WebSocket error:', error);
		};

		socket.onclose = () => {
			console.log('🔌 [WS] WebSocket disconnected');
			ws = null;
			// Try to reconnect after 3 seconds
			setTimeout(() => {
				console.log('🔄 [WS] Attempting to reconnect...');
				// The effect will re-run when ws changes to null
			}, 3000);
		};

		// Cleanup function - runs when component is destroyed
		return () => {
			if (socket && socket.readyState === WebSocket.OPEN) {
				console.log('🔌 [WS] Closing WebSocket connection (cleanup)');
				socket.close();
			}
		};
	});

	async function fetchLineStatus() {
		try {
			const response = await fetch('/api/plc');
			if (response.ok) {
				lineStatus = await response.json();
			}
		} catch (error) {
			console.error('Error fetching line status:', error);
		}
	}

	async function fetchAvailableLotes() {
		try {
			const response = await fetch('/api/plc');
			if (response.ok) {
				const data = await response.json();
				if (data.availableLotes) {
					availableLotes = data.availableLotes;
				}
			}
		} catch (error) {
			console.error('Error fetching available lotes:', error);
		}
	}

	async function startProduction(loteId: string) {
		try {
			const response = await fetch('/api/plc/start', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ loteId })
			});

			if (response.ok) {
				console.log('✅ Production started');
				await fetchLineStatus();
				await fetchAvailableLotes();
			} else {
				const error = await response.json();
				alert(error.message || 'Failed to start production');
			}
		} catch (error) {
			console.error('Error starting production:', error);
			alert('Error starting production');
		}
	}

	function openStopProductionModal() {
		stopProductionModal.show = true;
	}

	function closeStopProductionModal() {
		stopProductionModal.show = false;
	}

	async function confirmStopProduction() {
		closeStopProductionModal();

		try {
			const response = await fetch('/api/plc/stop', {
				method: 'DELETE'
			});

			if (response.ok) {
				console.log('⏹️ Production stopped');
				await fetchLineStatus();
				await fetchAvailableLotes();
			}
		} catch (error) {
			console.error('Error stopping production:', error);
		}
	}

	/**
	 * Stops production automatically when an error is detected
	 * This prevents cascading errors and unwanted registrations
	 */
	async function stopProductionDueToError() {
		try {
			const response = await fetch('/api/plc/stop', {
				method: 'DELETE'
			});

			if (response.ok) {
				console.log('⏹️ [Auto-Stop] Production paused due to error detection');
				await fetchLineStatus();
				await fetchAvailableLotes();
			}
		} catch (error) {
			console.error('❌ [Auto-Stop] Error stopping production:', error);
		}
	}

	function closeErrorModal() {
		errorModal = {
			show: false,
			message: '',
			imagePath: null,
			failureCode: 0,
			piezaIndex: 0,
			loteName: ''
		};
	}

	/**
	 * Resume production after reviewing the error
	 * User must manually restart production
	 */
	async function resumeProduction() {
		// Close modal first
		closeErrorModal();
		
		// Note: User must manually select and start a lot again from the UI
		// This is intentional to ensure proper review before continuing
		console.log('✅ [Modal] User acknowledged error. Production must be restarted manually.');
	}

	function getFailureTypeName(failureCode: number): string {
		switch (failureCode) {
			case 0: return 'Sin falla';
			case 1: return 'Test hipot falla';
			case 2: return 'Etiqueta incorrecta';
			case 3: return 'Modelo incorrecto';
			case 4: return 'Terminal incorrecta';
			default: return 'Falla desconocida';
		}
	}
</script>

<div class="production-page p-6 h-full overflow-auto">
	<div class="mb-6">
		<h1 class="text-3xl font-bold">Production Dashboard</h1>
		<p class="text-surface-600-400 mt-1">Real-time monitoring and control</p>
	</div>

	<!-- Line Status Card -->
	<div class="card variant-glass-surface p-6 mb-6">
		<header class="flex items-center justify-between mb-4">
			<h2 class="h3">Line Status</h2>
			<div class="flex items-center gap-2">
				<div
					class="w-3 h-3 rounded-full animate-pulse"
					class:bg-success-500={lineStatus.status === 'active'}
					class:bg-surface-500={lineStatus.status === 'idle'}
					class:bg-error-500={lineStatus.status === 'error'}
				></div>
				<span class="text-sm uppercase font-semibold" class:text-success-500={lineStatus.status === 'active'}>
					{lineStatus.status}
				</span>
			</div>
		</header>

		{#if lineStatus.status === 'idle'}
			<aside class="alert variant-filled-warning mb-4">
				<div class="alert-message">
					<p>⚠️ No active lot. Select a lot to start production.</p>
				</div>
			</aside>

			{#if canControl && availableLotes.length > 0}
				<div>
					<h3 class="h4 mb-3">Available Lots</h3>
					<div class="grid gap-3">
						{#each availableLotes as lote}
							<button
								class="card variant-ghost-surface p-6 hover:variant-soft-primary text-left transition-all touch-manipulation min-h-[120px]"
								onclick={() => startProduction(lote.id)}
							>
								<div class="flex justify-between items-start mb-2">
									<div class="font-bold text-xl flex items-center gap-2">
										<IconPlay size={20} />
										{lote.name}
									</div>
									<span class="badge variant-soft-success text-sm px-3 py-1">OPEN</span>
								</div>
								<div class="text-sm text-surface-600-400 mb-2">
									<span class="font-mono">{lote.receta?.ppn || 'N/A'}</span> - {lote.receta?.item_description || 'N/A'}
								</div>
								<div class="flex gap-4 text-sm">
									<div>
										<span class="text-surface-600-400">Target:</span>
										<span class="font-semibold">{lote.max_piezas_ok}</span>
									</div>
									<div>
										<span class="text-surface-600-400">Progress:</span>
										<span class="text-success-500 font-semibold">{lote.piezas_ok}</span>
										<span class="text-surface-600-400">/</span>
										<span class="text-error-500 font-semibold">{lote.piezas_fallas}</span>
									</div>
								</div>
							</button>
						{/each}
					</div>
				</div>
			{:else if !canControl}
				<p class="text-surface-600-400">You don't have permission to start production.</p>
			{:else}
				<p class="text-surface-600-400">No open lots available. Create a lot in Management first.</p>
			{/if}
		{:else if lineStatus.status === 'active' && lineStatus.lote}
			<aside class="alert variant-filled-success mb-4">
				<div class="alert-message">
					<p>✅ Production running: <strong>{lineStatus.lote.name}</strong></p>
				</div>
			</aside>

			<!-- Recipe Info -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
				<div class="space-y-1">
					<div class="text-sm text-surface-600-400">PPN</div>
					<div class="font-mono font-bold">{lineStatus.lote.receta.ppn}</div>
				</div>
				<div class="space-y-1">
					<div class="text-sm text-surface-600-400">Conductors</div>
					<div class="font-semibold">{lineStatus.lote.receta.cantidad_conductores}</div>
				</div>
				<div class="space-y-1 col-span-2">
					<div class="text-sm text-surface-600-400">Description</div>
					<div class="text-sm">{lineStatus.lote.receta.item_description}</div>
				</div>
			</div>

			<!-- Progress Bar -->
			<div class="mb-4">
				<div class="flex justify-between items-center mb-2">
					<span class="text-sm text-surface-600-400">Progress</span>
					<span class="font-bold">{lineStatus.lote.progress.toFixed(1)}%</span>
				</div>
				<div class="progress-bar h-3 bg-surface-200-800 rounded-full overflow-hidden">
					<div
						class="progress-fill h-full bg-gradient-to-r from-primary-500 to-success-500 transition-all duration-500"
						style="width: {lineStatus.lote.progress}%"
					></div>
				</div>
			</div>

			{#if canControl}
				<button 
					class="btn variant-filled-error text-lg px-6 py-4 min-h-[60px] touch-manipulation" 
					onclick={openStopProductionModal}
				>
					<IconSquare size={24} />
					<span>Stop Production</span>
				</button>
			{/if}
		{/if}
	</div>

	<!-- Metrics -->
	{#if canViewMetrics && lineStatus.status === 'active'}
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
			<div class="card variant-filled-success/10 p-4">
				<div class="text-sm text-surface-600-400 mb-1">OK Pieces</div>
				<div class="text-3xl font-bold text-success-500">{metrics.ok}</div>
			</div>
			<div class="card variant-filled-error/10 p-4">
				<div class="text-sm text-surface-600-400 mb-1">NOK Pieces</div>
				<div class="text-3xl font-bold text-error-500">{metrics.nok}</div>
			</div>
			<div class="card variant-glass-surface p-4">
				<div class="text-sm text-surface-600-400 mb-1">Efficiency</div>
				<div class="text-3xl font-bold">{metrics.efficiency.toFixed(1)}%</div>
			</div>
			<div class="card variant-glass-surface p-4">
				<div class="text-sm text-surface-600-400 mb-1">Accuracy</div>
				<div class="text-3xl font-bold">{metrics.accuracy.toFixed(1)}%</div>
			</div>
		</div>
	{/if}

	<!-- Real-time PLC Data -->
	{#if plcData}
		<div class="card variant-glass-surface p-6 mb-6">
			<h2 class="h3 mb-4">Real-time PLC Data</h2>
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
				<div class="space-y-1">
					<div class="text-sm text-surface-600-400">Line Status</div>
					<div class="badge variant-soft">{plcData.lineStatus}</div>
				</div>
				<div class="space-y-1">
					<div class="text-sm text-surface-600-400">Piece Status</div>
					<span
						class="badge"
						class:variant-filled-success={plcData.pieceStatus === 'OK'}
						class:variant-filled-error={plcData.pieceStatus === 'NOK'}
					>
						{plcData.pieceStatus}
					</span>
				</div>
				<div class="space-y-1">
					<div class="text-sm text-surface-600-400">Failure Type</div>
					<div class="text-sm">{plcData.failureType}</div>
				</div>
				<div class="space-y-1">
					<div class="text-sm text-surface-600-400">Raw Data</div>
					<div class="font-mono text-xs">[{plcData.rawData?.join(', ') || 'N/A'}]</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Recent Pieces -->
	{#if lineStatus.status === 'active' && recentPieces.length > 0}
		<div class="card variant-glass-surface p-6">
			<h2 class="h3 mb-4">Recent Pieces</h2>
			<div class="table-container">
				<table class="table table-hover">
					<thead>
						<tr>
							<th>Index</th>
							<th>Status</th>
							<th>Processed At</th>
							<th>Raw Data</th>
						</tr>
					</thead>
					<tbody>
						{#each recentPieces as pieza (pieza.id)}
							<tr class:animate-pulse={pieza.isNew}>
								<td class="font-mono">#{pieza.indice}</td>
								<td>
									<span
										class="badge"
										class:variant-filled-success={pieza.ok}
										class:variant-filled-error={!pieza.ok}
									>
										{pieza.ok ? '✓ OK' : '✗ NOK'}
									</span>
									{#if pieza.imagen_path === 'pending'}
										<span class="badge variant-soft-warning ml-2">📸 Awaiting image</span>
									{:else if pieza.imagen_path && pieza.imagen_path !== ''}
										<span class="badge variant-soft-success ml-2">🖼️ Image saved</span>
									{/if}
								</td>
								<td class="text-sm">{new Date(pieza.processed_at).toLocaleString()}</td>
								<td class="font-mono text-xs">[{pieza.resultado_bits?.join(', ') || 'N/A'}]</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</div>

<!-- Error Modal -->
{#if errorModal.show}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div 
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
		onclick={closeErrorModal}
	>
		<div 
			class="card variant-filled-error w-full max-w-2xl max-h-[90vh] overflow-auto m-4 p-0"
			onclick={(e) => e.stopPropagation()}
		>
			<!-- Modal Header -->
			<header class="card-header bg-error-500 text-white p-6">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-4">
						<IconAlertTriangle size={48} class="animate-pulse" />
						<div>
							<h3 class="text-2xl font-bold">Falla en Producción</h3>
							<p class="text-base opacity-90 mt-1">Lote: {errorModal.loteName} - Pieza #{errorModal.piezaIndex}</p>
						</div>
					</div>
					<button 
						class="btn-icon variant-filled hover:variant-filled-primary w-12 h-12 touch-manipulation"
						onclick={closeErrorModal}
						aria-label="Cerrar"
					>
						<IconX size={28} />
					</button>
				</div>
			</header>

			<!-- Modal Body -->
			<section class="p-6 space-y-4">
				<!-- Failure Information -->
				<div class="card variant-ghost-error p-4">
					<div class="grid grid-cols-2 gap-4">
						<div>
							<p class="text-sm text-surface-600-400 mb-1">Tipo de Falla</p>
							<p class="font-bold text-lg">{getFailureTypeName(errorModal.failureCode)}</p>
						</div>
						<div>
							<p class="text-sm text-surface-600-400 mb-1">Código de Falla</p>
							<p class="font-bold text-lg">#{errorModal.failureCode}</p>
						</div>
					</div>
				</div>

				<!-- Image -->
				{#if errorModal.imagePath}
					<div class="card variant-glass-surface p-2">
						<img 
							src={errorModal.imagePath} 
							alt="Imagen de la falla"
							class="w-full h-auto rounded-lg"
						/>
					</div>
				{:else}
					<div class="card variant-ghost-surface p-8 text-center">
						<p class="text-surface-600-400">⏳ Cargando imagen...</p>
					</div>
				{/if}

				<!-- Instructions -->
				<div class="alert variant-filled-error">
					<div class="alert-message">
						<h4 class="font-bold mb-2">🛑 Producción Pausada Automáticamente</h4>
						<p class="text-sm">
							Se ha detectado una falla en la pieza #{errorModal.piezaIndex} y la producción ha sido pausada para prevenir errores en cascada.
						</p>
						<p class="text-sm mt-2 font-semibold">
							⚠️ Revise la imagen, tome las acciones correctivas necesarias y reinicie la producción manualmente cuando esté listo.
						</p>
					</div>
				</div>
			</section>

			<!-- Modal Footer -->
			<footer class="card-footer bg-surface-200-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 p-6">
				<div class="text-base text-warning-500 flex items-center gap-2">
					<IconAlertCircle size={20} />
					<span><span class="font-bold">Nota:</span> Debe reiniciar la producción manualmente</span>
				</div>
				<div class="flex gap-3 w-full md:w-auto">
					<button 
						class="btn variant-filled-error flex-1 md:flex-none text-lg px-6 py-4 min-h-[60px] touch-manipulation"
						onclick={closeErrorModal}
					>
						<IconPause size={24} />
						<span>Mantener Pausada</span>
					</button>
					<button 
						class="btn variant-filled-success flex-1 md:flex-none text-lg px-6 py-4 min-h-[60px] touch-manipulation"
						onclick={resumeProduction}
					>
						<IconCheckCircle size={24} />
						<span>He Revisado</span>
					</button>
				</div>
			</footer>
		</div>
	</div>
{/if}

<!-- Stop Production Confirmation Modal -->
{#if stopProductionModal.show}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div 
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
		onclick={closeStopProductionModal}
	>
		<div 
			class="card variant-filled-warning w-full max-w-md p-0"
			onclick={(e) => e.stopPropagation()}
		>
			<!-- Modal Header -->
			<header class="card-header bg-warning-500 text-surface-900 p-6">
				<div class="flex items-center gap-4">
					<IconAlertCircle size={40} class="animate-pulse" />
					<div>
						<h3 class="text-2xl font-bold">Confirmar Detención</h3>
						<p class="text-base opacity-90 mt-1">¿Está seguro de detener la producción?</p>
					</div>
				</div>
			</header>

			<!-- Modal Body -->
			<section class="p-6 space-y-4">
				<div class="alert variant-ghost-warning">
					<div class="alert-message">
						<p class="text-base">
							Al detener la producción, el sistema dejará de procesar piezas. Deberá seleccionar un lote manualmente para reiniciar.
						</p>
					</div>
				</div>

				{#if lineStatus.lote}
					<div class="card variant-glass-surface p-4">
						<p class="text-sm text-surface-600-400 mb-2">Lote Actual</p>
						<p class="font-bold text-lg">{lineStatus.lote.name}</p>
						<p class="text-sm text-surface-600-400 mt-2">
							Progreso: {lineStatus.lote.piezasOk} OK / {lineStatus.lote.piezasFallas} NOK
						</p>
					</div>
				{/if}
			</section>

			<!-- Modal Footer -->
			<footer class="card-footer bg-surface-200-800 flex gap-3 p-6">
				<button 
					class="btn variant-ghost-surface flex-1 text-lg px-6 py-4 min-h-[60px] touch-manipulation"
					onclick={closeStopProductionModal}
				>
					<IconX size={24} />
					<span>Cancelar</span>
				</button>
				<button 
					class="btn variant-filled-error flex-1 text-lg px-6 py-4 min-h-[60px] touch-manipulation"
					onclick={confirmStopProduction}
				>
					<IconSquare size={24} />
					<span>Detener</span>
				</button>
			</footer>
		</div>
	</div>
{/if}

<style>
	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
			background-color: transparent;
		}
		50% {
			opacity: 0.8;
			background-color: rgba(var(--color-primary-500) / 0.1);
		}
	}

	.animate-pulse {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1);
	}

	/* Enhanced touch targets */
	.touch-manipulation {
		-webkit-tap-highlight-color: transparent;
		touch-action: manipulation;
	}
</style>

