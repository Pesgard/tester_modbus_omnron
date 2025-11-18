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
	recentPieces = recentPieces.map((pieza: any) => ({
		...pieza,
		images:
			pieza.images ??
			(pieza.imagen_path && pieza.imagen_path !== '' && pieza.imagen_path !== 'pending'
				? [pieza.imagen_path]
				: []),
		awaitingImage: pieza.awaitingImage ?? false,
		failureCode: pieza.failureCode ?? 0,
		loteName: pieza.loteName ?? pieza?.lote?.name ?? lineStatus.lote?.name ?? ''
	}));

	// Error modal state
	let errorModal = $state<{
		show: boolean;
		message: string;
		imageList: string[];
		failureCode: number;
		piezaIndex: number;
		loteName: string;
	}>({
		show: false,
		message: '',
		imageList: [],
		failureCode: 0,
		piezaIndex: 0,
		loteName: ''
	});

	// Emergency stop modal state
	let emergencyStopModal = $state<{
		show: boolean;
		reason: string;
		message: string;
		timestamp: string;
		loteId: string;
		loteName: string;
	}>({
		show: false,
		reason: '',
		message: '',
		timestamp: '',
		loteId: '',
		loteName: ''
	});

	// Model mismatch modal state
	let modelMismatchModal = $state<{
		show: boolean;
		expectedModelId: number;
		receivedModelId: number;
		loteName: string;
		recipePpn: string;
		message: string;
		timestamp: string;
	}>({
		show: false,
		expectedModelId: 0,
		receivedModelId: 0,
		loteName: '',
		recipePpn: '',
		message: '',
		timestamp: ''
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
							images: [],
							awaitingImage: message.payload.hasImage,
							failureCode: message.payload.failureCode ?? 0,
							loteName: message.payload.loteName ?? '',
							processed_at: new Date().toISOString(),
							resultado_bits: message.payload.parsed?.rawData || [],
							isNew: true
						};

						// Add new piece to the top of the list
						recentPieces = [newPiece, ...recentPieces.slice(0, 19)];
						console.log('📝 [WS] Recent pieces updated, count:', recentPieces.length);

						// Remove isNew flag after animation (2 seconds)
						setTimeout(() => {
							const index = recentPieces.findIndex((p) => p.id === newPiece.id);
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
							updatedLote.progress =
								updatedLote.maxPiezasOk > 0
									? (updatedLote.piezasOk / updatedLote.maxPiezasOk) * 100
									: 0;

							// Force reactive update by creating new object
							lineStatus = { ...lineStatus, lote: updatedLote };
							console.log('📊 [WS] Line status updated:', updatedLote);
						}

						if (!message.payload.ok && (message.payload.failureCode ?? 0) > 0) {
							console.warn('⚠️ [WS] Pausing production due to detected failure');
							stopProductionDueToError();

							errorModal = {
								show: true,
								message: `Falla detectada en pieza #${message.payload.index}`,
								imageList: [],
								failureCode: message.payload.failureCode || 0,
								piezaIndex: message.payload.index,
								loteName: message.payload.loteName || ''
							};
						}
						break;

					case 'awaiting-image':
						console.log('📸 [WS] Awaiting image for piece:', message.payload.piezaIndex);
						// Mark piece as waiting for image
						const waitingIndex = recentPieces.findIndex(
							(p) => p.indice === message.payload.piezaIndex && p.lote_id === message.payload.loteId
						);
						if (waitingIndex !== -1) {
							const updated = [...recentPieces];
							updated[waitingIndex] = {
								...updated[waitingIndex],
								imagen_path: 'pending',
								awaitingImage: true
							};
							recentPieces = updated;
						}
						break;

					case 'piece-images-linked': {
						console.log('🖼️ [WS] Piece images linked:', message.payload);
						const { piezaIndex, loteId, images } = message.payload;

						console.log('🔍 [Debug] Checking modal:', {
							modalOpen: errorModal.show,
							modalPiezaIndex: errorModal.piezaIndex,
							receivedPiezaIndex: piezaIndex,
							imagesCount: images?.length || 0
						});

						const pieceIdx = recentPieces.findIndex(
							(p) => p.indice === piezaIndex && p.lote_id === loteId
						);

						if (pieceIdx !== -1) {
							const updatedPieces = [...recentPieces];
							const targetPiece = updatedPieces[pieceIdx];
							updatedPieces[pieceIdx] = {
								...targetPiece,
								imagen_path: images?.[0] || targetPiece.imagen_path,
								images: images || [],
								awaitingImage: false
							};
							recentPieces = updatedPieces;
						}

						// Actualizar el modal de error si está abierto y corresponde a esta pieza
						if (errorModal.show && errorModal.piezaIndex === piezaIndex) {
							console.log('✅ [Modal] Updating images in error modal:', images);
							errorModal = {
								...errorModal,
								imageList: images || []
							};
						}

						break;
					}

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

					case 'emergency-stop':
						console.log('🚨 [WS] Emergency stop:', message.payload);

						// Show emergency stop modal immediately
						emergencyStopModal = {
							show: true,
							reason: message.payload.reason,
							message: message.payload.message,
							timestamp: message.payload.timestamp,
							loteId: message.payload.loteId,
							loteName: message.payload.loteName
						};

						// Clear recent pieces and update status
						recentPieces = [];
						fetchLineStatus();
						fetchAvailableLotes();
						break;

					case 'model-mismatch':
						console.error('🚨 [WS] Model ID mismatch:', message.payload);

						// Show model mismatch modal
						modelMismatchModal = {
							show: true,
							expectedModelId: message.payload.expectedModelId,
							receivedModelId: message.payload.receivedModelId,
							loteName: message.payload.loteName,
							recipePpn: message.payload.recipePpn,
							message: message.payload.message,
							timestamp: message.payload.timestamp
						};
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
			imageList: [],
			failureCode: 0,
			piezaIndex: 0,
			loteName: ''
		};
	}

	function closeEmergencyStopModal() {
		emergencyStopModal = {
			show: false,
			reason: '',
			message: '',
			timestamp: '',
			loteId: '',
			loteName: ''
		};
	}

	function closeModelMismatchModal() {
		modelMismatchModal = {
			show: false,
			expectedModelId: 0,
			receivedModelId: 0,
			loteName: '',
			recipePpn: '',
			message: '',
			timestamp: ''
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
			case 0:
				return 'Sin falla';
			case 1:
				return 'Test hipot falla';
			case 2:
				return 'Etiqueta incorrecta';
			case 3:
				return 'Modelo incorrecto';
			case 4:
				return 'Terminal incorrecta';
			default:
				return 'Falla desconocida';
		}
	}

	// Image carousel refs and functions
	let carousel: HTMLDivElement | null = $state(null);
	let btnLeft: HTMLButtonElement | null = $state(null);
	let btnRight: HTMLButtonElement | null = $state(null);

	function left() {
		if (!carousel) return;
		const x =
			carousel.scrollLeft === 0
				? carousel.clientWidth * carousel.childElementCount
				: carousel.scrollLeft - carousel.clientWidth;
		carousel.scroll(x, 0);
	}

	function right() {
		if (!carousel) return;
		const x =
			carousel.scrollLeft === carousel.scrollWidth - carousel.clientWidth
				? 0
				: carousel.scrollLeft + carousel.clientWidth;
		carousel.scroll(x, 0);
	}

	function goTo(index: number) {
		if (carousel) carousel.scroll(carousel.clientWidth * index, 0);
	}
</script>

<div class="production-page h-full overflow-auto p-6">
	<div class="mb-6">
		<h1 class="text-3xl font-bold">Production Dashboard</h1>
		<p class="mt-1 text-surface-600-400">Real-time monitoring and control</p>
	</div>

	<!-- Line Status Card -->
	<div class="variant-glass-surface mb-6 card p-6">
		<header class="mb-4 flex items-center justify-between">
			<h2 class="h3">Line Status</h2>
			<div class="flex items-center gap-2">
				<div
					class="h-3 w-3 animate-pulse rounded-full"
					class:bg-success-500={lineStatus.status === 'active'}
					class:bg-surface-500={lineStatus.status === 'idle'}
					class:bg-error-500={lineStatus.status === 'error'}
				></div>
				<span
					class="text-sm font-semibold uppercase"
					class:text-success-500={lineStatus.status === 'active'}
				>
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
					<h3 class="mb-3 h4">Available Lots</h3>
					<div class="grid gap-3">
						{#each availableLotes as lote}
							<button
								class="variant-ghost-surface hover:variant-soft-primary min-h-[120px] touch-manipulation card p-6 text-left transition-all"
								onclick={() => startProduction(lote.id)}
							>
								<div class="mb-2 flex items-start justify-between">
									<div class="flex items-center gap-2 text-xl font-bold">
										<IconPlay size={20} />
										{lote.name}
									</div>
									<span class="variant-soft-success badge px-3 py-1 text-sm">OPEN</span>
								</div>
								<div class="mb-2 text-sm text-surface-600-400">
									<span class="font-mono">{lote.receta?.ppn || 'N/A'}</span> - {lote.receta
										?.item_description || 'N/A'}
								</div>
								<div class="flex gap-4 text-sm">
									<div>
										<span class="text-surface-600-400">Target:</span>
										<span class="font-semibold">{lote.max_piezas_ok}</span>
									</div>
									<div>
										<span class="text-surface-600-400">Progress:</span>
										<span class="font-semibold text-success-500">{lote.piezas_ok}</span>
										<span class="text-surface-600-400">/</span>
										<span class="font-semibold text-error-500">{lote.piezas_fallas}</span>
									</div>
								</div>
							</button>
						{/each}
					</div>
				</div>
			{:else if !canControl}
				<p class="text-surface-600-400">You don't have permission to start production.</p>
			{:else}
				<p class="text-surface-600-400">
					No open lots available. Create a lot in Management first.
				</p>
			{/if}
		{:else if lineStatus.status === 'active' && lineStatus.lote}
			<aside class="alert variant-filled-success mb-4">
				<div class="alert-message">
					<p>✅ Production running: <strong>{lineStatus.lote.name}</strong></p>
				</div>
			</aside>

			<!-- Recipe Info -->
			<div class="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
				<div class="space-y-1">
					<div class="text-sm text-surface-600-400">PPN</div>
					<div class="font-mono font-bold">{lineStatus.lote.receta.ppn}</div>
				</div>
				<div class="space-y-1">
					<div class="text-sm text-surface-600-400">Conductors</div>
					<div class="font-semibold">{lineStatus.lote.receta.cantidad_conductores}</div>
				</div>
				<div class="col-span-2 space-y-1">
					<div class="text-sm text-surface-600-400">Description</div>
					<div class="text-sm">{lineStatus.lote.receta.item_description}</div>
				</div>
			</div>

			<!-- Progress Bar -->
			<div class="mb-4">
				<div class="mb-2 flex items-center justify-between">
					<span class="text-sm text-surface-600-400">Progress</span>
					<span class="font-bold">{lineStatus.lote.progress.toFixed(1)}%</span>
				</div>
				<div class="progress-bar h-3 overflow-hidden rounded-full bg-surface-200-800">
					<div
						class="progress-fill h-full bg-gradient-to-r from-primary-500 to-success-500 transition-all duration-500"
						style="width: {lineStatus.lote.progress}%"
					></div>
				</div>
			</div>

			{#if canControl}
				<button
					class="variant-filled-error btn min-h-[60px] touch-manipulation px-6 py-4 text-lg"
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
		<div class="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
			<div class="variant-filled-success/10 card p-4">
				<div class="mb-1 text-sm text-surface-600-400">OK Pieces</div>
				<div class="text-3xl font-bold text-success-500">{metrics.ok}</div>
			</div>
			<div class="variant-filled-error/10 card p-4">
				<div class="mb-1 text-sm text-surface-600-400">NOK Pieces</div>
				<div class="text-3xl font-bold text-error-500">{metrics.nok}</div>
			</div>
			<div class="variant-glass-surface card p-4">
				<div class="mb-1 text-sm text-surface-600-400">Efficiency</div>
				<div class="text-3xl font-bold">{metrics.efficiency.toFixed(1)}%</div>
			</div>
			<div class="variant-glass-surface card p-4">
				<div class="mb-1 text-sm text-surface-600-400">Accuracy</div>
				<div class="text-3xl font-bold">{metrics.accuracy.toFixed(1)}%</div>
			</div>
		</div>
	{/if}

	<!-- Real-time PLC Data -->
	{#if plcData}
		<div class="variant-glass-surface mb-6 card p-6">
			<h2 class="mb-4 h3">Real-time PLC Data</h2>
			<div class="grid grid-cols-2 gap-4 md:grid-cols-4">
				<div class="space-y-1">
					<div class="text-sm text-surface-600-400">Line Status</div>
					<div class="variant-soft badge">{plcData.lineStatus}</div>
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
		<div class="variant-glass-surface card p-6">
			<h2 class="mb-4 h3">Recent Pieces</h2>
			<div class="table-container">
				<table class="table-hover table">
					<thead>
						<tr>
							<th>Index</th>
							<th>Status</th>
							<th>Imágenes</th>
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
										<span class="variant-soft-warning ml-2 badge">📸 Awaiting image</span>
									{:else if pieza.imagen_path && pieza.imagen_path !== ''}
										<span class="variant-soft-success ml-2 badge">🖼️ Image saved</span>
									{/if}
								</td>
								<td>
									{#if pieza.awaitingImage}
										<span class="text-sm text-surface-500">—</span>
									{:else if pieza.images && pieza.images.length > 0}
										<span class="variant-soft-success badge">
											{pieza.images.length === 1 ? '1 imagen' : `${pieza.images.length} imágenes`}
										</span>
									{:else if pieza.imagen_path && pieza.imagen_path !== ''}
										<span class="variant-soft-success badge">1 imagen</span>
									{:else}
										<span class="text-sm text-surface-500">—</span>
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

<!-- Modal de Error con Carrusel (Reemplazar el modal existente) -->

{#if errorModal.show}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
		onclick={closeErrorModal}
	>
		<div
			class="variant-filled-error m-4 max-h-[90vh] w-full max-w-2xl overflow-auto card p-0"
			onclick={(e) => e.stopPropagation()}
		>
			<!-- Modal Header -->
			<header class="card-header bg-error-500 p-6 text-white">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-4">
						<IconAlertTriangle size={48} class="animate-pulse" />
						<div>
							<h3 class="text-2xl font-bold">Falla en Producción</h3>
							<p class="mt-1 text-base opacity-90">
								Lote: {errorModal.loteName} - Pieza #{errorModal.piezaIndex}
							</p>
						</div>
					</div>
					<button
						class="variant-filled hover:variant-filled-primary btn-icon h-12 w-12 touch-manipulation"
						onclick={closeErrorModal}
						aria-label="Cerrar"
					>
						<IconX size={28} />
					</button>
				</div>
			</header>

			<!-- Modal Body -->
			<section class="space-y-4 p-6">
				<!-- Failure Information -->
				<div class="variant-ghost-error card p-4">
					<div class="grid grid-cols-2 gap-4">
						<div>
							<p class="mb-1 text-sm text-surface-600-400">Tipo de Falla</p>
							<p class="text-lg font-bold">{getFailureTypeName(errorModal.failureCode)}</p>
						</div>
						<div>
							<p class="mb-1 text-sm text-surface-600-400">Código de Falla</p>
							<p class="text-lg font-bold">#{errorModal.failureCode}</p>
						</div>
					</div>
				</div>

				<!-- Image Gallery -->
				{#if errorModal.imageList.length > 0}
					<div class="variant-glass-surface card p-4">
						<!-- Carousel -->
						<div class="grid grid-cols-[auto_1fr_auto] items-center gap-4">
							<!-- Left Button -->
							<button bind:this={btnLeft} onclick={left} class="btn-icon preset-filled"> ← </button>

							<!-- Image Container -->
							<div
								bind:this={carousel}
								class="flex max-w-full snap-x snap-mandatory overflow-x-auto scroll-smooth rounded-container"
							>
								{#each errorModal.imageList as img, i}
									<img
										class="max-h-[70vh] w-[900px] snap-center rounded-container object-contain"
										src={img}
										alt={`img-${i}`}
									/>
								{/each}
							</div>

							<!-- Right Button -->
							<button bind:this={btnRight} onclick={right} class="btn-icon preset-filled">
								→
							</button>
						</div>

						<!-- Thumbnails -->
						{#if errorModal.imageList.length > 1}
							<div class="mt-4 grid grid-cols-6 gap-2">
								{#each errorModal.imageList as img, i}
									<button onclick={() => goTo(i)} class="hover:brightness-125">
										<img class="rounded-container" src={img} alt={`thumb-${i}`} />
									</button>
								{/each}
							</div>
						{/if}
					</div>
				{:else}
					<div class="variant-ghost-surface card p-8 text-center">
						<!-- <p class="text-surface-600-400">Sin imágenes asociadas para esta pieza.</p> -->
					</div>
				{/if}

				<!-- Instructions -->
				<div class="alert variant-filled-error">
					<div class="alert-message">
						<h4 class="mb-2 font-bold">🛑 Producción Pausada Automáticamente</h4>
						<p class="text-sm">
							Se ha detectado una falla en la pieza #{errorModal.piezaIndex} y la producción ha sido
							pausada para prevenir errores en cascada.
						</p>
						<p class="mt-2 text-sm font-semibold">
							⚠️ Revise la imagen, tome las acciones correctivas necesarias y reinicie la producción
							manualmente cuando esté listo.
						</p>
					</div>
				</div>
			</section>

			<!-- Modal Footer -->
			<footer
				class="card-footer flex flex-col items-start justify-between gap-4 bg-surface-200-800 p-6 md:flex-row md:items-center"
			>
				<div class="flex items-center gap-2 text-base text-warning-500">
					<IconAlertCircle size={20} />
					<span><span class="font-bold">Nota:</span> Debe reiniciar la producción manualmente</span>
				</div>
				<div class="flex w-full gap-3 md:w-auto">
					<button
						class="variant-filled-error btn min-h-[60px] flex-1 touch-manipulation px-6 py-4 text-lg md:flex-none"
						onclick={closeErrorModal}
					>
						<IconPause size={24} />
						<span>Mantener Pausada</span>
					</button>
					<button
						class="variant-filled-success btn min-h-[60px] flex-1 touch-manipulation px-6 py-4 text-lg md:flex-none"
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
<!-- Emergency Stop Modal -->
{#if emergencyStopModal.show}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
		onclick={closeEmergencyStopModal}
	>
		<div
			class="variant-filled-error m-4 max-h-[90vh] w-full max-w-2xl overflow-auto card p-0"
			onclick={(e) => e.stopPropagation()}
		>
			<!-- Modal Header -->
			<header class="card-header bg-error-500 p-6 text-white">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-4">
						<IconAlertTriangle size={48} class="animate-pulse" />
						<div>
							<h3 class="text-2xl font-bold">🚨 PARO DE EMERGENCIA</h3>
							<p class="mt-1 text-base opacity-90">Estado: {emergencyStopModal.reason}</p>
						</div>
					</div>
					<button
						class="variant-filled hover:variant-filled-primary btn-icon h-12 w-12 touch-manipulation"
						onclick={closeEmergencyStopModal}
						aria-label="Cerrar"
					>
						<IconX size={28} />
					</button>
				</div>
			</header>

			<!-- Modal Body -->
			<section class="space-y-4 p-6">
				<!-- Emergency Information -->
				<div class="variant-ghost-error card p-4">
					<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
						<div>
							<p class="mb-1 text-sm text-surface-600-400">Motivo</p>
							<p class="text-lg font-bold">{emergencyStopModal.reason}</p>
						</div>
						<div>
							<p class="mb-1 text-sm text-surface-600-400">Lote Afectado</p>
							<p class="text-lg font-bold">{emergencyStopModal.loteName}</p>
						</div>
					</div>
					<div class="mt-4">
						<p class="mb-1 text-sm text-surface-600-400">Mensaje</p>
						<p class="text-base font-semibold">{emergencyStopModal.message}</p>
					</div>
					<div class="mt-4">
						<p class="mb-1 text-sm text-surface-600-400">Timestamp</p>
						<p class="font-mono text-sm">
							{new Date(emergencyStopModal.timestamp).toLocaleString()}
						</p>
					</div>
				</div>

				<!-- Instructions -->
				<div class="alert variant-filled-error">
					<div class="alert-message">
						<h4 class="mb-2 font-bold">🛑 PRODUCCIÓN DETENIDA POR MANTENIMIENTO</h4>
						<p class="text-sm">
							El PLC ha enviado una señal de mantenimiento. La producción se ha detenido
							inmediatamente para garantizar la seguridad del equipo y personal.
						</p>
						<p class="mt-2 text-sm font-semibold">
							⚠️ Complete las tareas de mantenimiento y reinicie la producción manualmente cuando
							esté listo.
						</p>
					</div>
				</div>

				<!-- Safety Notice -->
				<div class="variant-glass-surface card border-l-4 border-warning-500 p-4">
					<div class="flex items-start gap-3">
						<IconAlertCircle size={24} class="mt-1 text-warning-500" />
						<div>
							<h5 class="mb-2 font-bold text-warning-500">Nota de Seguridad</h5>
							<p class="text-sm text-surface-600-400">
								Este paro de emergencia se activó automáticamente cuando el PLC detectó condiciones
								de mantenimiento. Verifique el estado del equipo antes de reiniciar la producción.
							</p>
						</div>
					</div>
				</div>
			</section>

			<!-- Modal Footer -->
			<footer
				class="card-footer flex flex-col items-start justify-between gap-4 bg-surface-200-800 p-6 md:flex-row md:items-center"
			>
				<div class="flex items-center gap-2 text-base text-warning-500">
					<IconAlertCircle size={20} />
					<span
						><span class="font-bold">Importante:</span> Producción detenida por mantenimiento</span
					>
				</div>
				<div class="flex w-full gap-3 md:w-auto">
					<button
						class="variant-filled-error btn min-h-[60px] flex-1 touch-manipulation px-6 py-4 text-lg md:flex-none"
						onclick={closeEmergencyStopModal}
					>
						<IconPause size={24} />
						<span>Entendido</span>
					</button>
				</div>
			</footer>
		</div>
	</div>
{/if}

<!-- Model Mismatch Modal -->
{#if modelMismatchModal.show}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
		onclick={closeModelMismatchModal}
	>
		<div
			class="variant-filled-error m-4 max-h-[90vh] w-full max-w-2xl overflow-auto card p-0"
			onclick={(e) => e.stopPropagation()}
		>
			<!-- Modal Header -->
			<header class="card-header bg-error-500 p-6 text-white">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-4">
						<IconAlertTriangle size={48} class="animate-pulse" />
						<div>
							<h3 class="text-2xl font-bold">🚨 ERROR DE MODELO ID</h3>
							<p class="mt-1 text-base opacity-90">Mismatch detectado en producción</p>
						</div>
					</div>
					<button
						class="variant-filled hover:variant-filled-primary btn-icon h-12 w-12 touch-manipulation"
						onclick={closeModelMismatchModal}
						aria-label="Cerrar"
					>
						<IconX size={28} />
					</button>
				</div>
			</header>

			<!-- Modal Body -->
			<section class="space-y-4 p-6">
				<!-- Error Information -->
				<div class="variant-ghost-error card p-4">
					<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
						<div>
							<p class="mb-1 text-sm text-surface-600-400">Lote</p>
							<p class="text-lg font-bold">{modelMismatchModal.loteName}</p>
						</div>
						<div>
							<p class="mb-1 text-sm text-surface-600-400">Receta</p>
							<p class="font-mono text-lg font-bold">{modelMismatchModal.recipePpn}</p>
						</div>
					</div>
					<div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
						<div>
							<p class="mb-1 text-sm text-surface-600-400">Model ID Esperado</p>
							<p class="text-lg font-bold text-success-500">{modelMismatchModal.expectedModelId}</p>
						</div>
						<div>
							<p class="mb-1 text-sm text-surface-600-400">Model ID Recibido</p>
							<p class="text-lg font-bold text-error-500">{modelMismatchModal.receivedModelId}</p>
						</div>
					</div>
					<div class="mt-4">
						<p class="mb-1 text-sm text-surface-600-400">Timestamp</p>
						<p class="font-mono text-sm">
							{new Date(modelMismatchModal.timestamp).toLocaleString()}
						</p>
					</div>
				</div>

				<!-- Error Details -->
				<div class="alert variant-filled-error">
					<div class="alert-message">
						<h4 class="mb-2 font-bold">❌ PIEZA RECHAZADA</h4>
						<p class="text-sm">
							El PLC envió un Model ID ({modelMismatchModal.receivedModelId}) que no coincide con el
							lote activo ({modelMismatchModal.expectedModelId}).
						</p>
						<p class="mt-2 text-sm font-semibold">
							🛡️ La pieza NO se guardó en la base de datos para mantener la integridad de los datos.
						</p>
					</div>
				</div>

				<!-- Instructions -->
				<div class="variant-glass-surface card border-l-4 border-warning-500 p-4">
					<div class="flex items-start gap-3">
						<IconAlertCircle size={24} class="mt-1 text-warning-500" />
						<div>
							<h5 class="mb-2 font-bold text-warning-500">Acción Requerida</h5>
							<p class="text-sm text-surface-600-400">
								Verifique la configuración del PLC y asegúrese de que esté enviando el Model ID
								correcto ({modelMismatchModal.expectedModelId}) para el lote activo ({modelMismatchModal.loteName}).
							</p>
						</div>
					</div>
				</div>

				<!-- Model ID Reference -->
				<div class="variant-ghost-surface card p-4">
					<h5 class="mb-3 font-bold">📋 Referencia de Model IDs</h5>
					<div class="grid grid-cols-1 gap-2 text-sm md:grid-cols-2">
						<div class="flex justify-between">
							<span class="font-mono">ID 1:</span>
							<span>1020746 (2 cond.)</span>
						</div>
						<div class="flex justify-between">
							<span class="font-mono">ID 2:</span>
							<span>1020746-02 (2 cond.)</span>
						</div>
						<div class="flex justify-between">
							<span class="font-mono">ID 3:</span>
							<span>1020746-03 (2 cond.)</span>
						</div>
						<div class="flex justify-between">
							<span class="font-mono">ID 4:</span>
							<span>1020746-04 (2 cond.)</span>
						</div>
						<div class="flex justify-between">
							<span class="font-mono">ID 5:</span>
							<span>1020746-05 (2 cond.)</span>
						</div>
						<div class="flex justify-between">
							<span class="font-mono">ID 6:</span>
							<span>1020746-06 (2 cond.)</span>
						</div>
						<div class="flex justify-between">
							<span class="font-mono">ID 7:</span>
							<span>698330001 (4 cond.)</span>
						</div>
					</div>
				</div>
			</section>

			<!-- Modal Footer -->
			<footer
				class="card-footer flex flex-col items-start justify-between gap-4 bg-surface-200-800 p-6 md:flex-row md:items-center"
			>
				<div class="flex items-center gap-2 text-base text-warning-500">
					<IconAlertCircle size={20} />
					<span><span class="font-bold">Protegido:</span> Datos incorrectos rechazados</span>
				</div>
				<div class="flex w-full gap-3 md:w-auto">
					<button
						class="variant-filled-error btn min-h-[60px] flex-1 touch-manipulation px-6 py-4 text-lg md:flex-none"
						onclick={closeModelMismatchModal}
					>
						<IconCheckCircle size={24} />
						<span>Entendido</span>
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
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
		onclick={closeStopProductionModal}
	>
		<div
			class="variant-filled-warning w-full max-w-md card p-0"
			onclick={(e) => e.stopPropagation()}
		>
			<!-- Modal Header -->
			<header class="card-header bg-warning-500 p-6 text-surface-900">
				<div class="flex items-center gap-4">
					<IconAlertCircle size={40} class="animate-pulse" />
					<div>
						<h3 class="text-2xl font-bold">Confirmar Detención</h3>
						<p class="mt-1 text-base opacity-90">¿Está seguro de detener la producción?</p>
					</div>
				</div>
			</header>

			<!-- Modal Body -->
			<section class="space-y-4 p-6">
				<div class="alert variant-ghost-warning">
					<div class="alert-message">
						<p class="text-base">
							Al detener la producción, el sistema dejará de procesar piezas. Deberá seleccionar un
							lote manualmente para reiniciar.
						</p>
					</div>
				</div>

				{#if lineStatus.lote}
					<div class="variant-glass-surface card p-4">
						<p class="mb-2 text-sm text-surface-600-400">Lote Actual</p>
						<p class="text-lg font-bold">{lineStatus.lote.name}</p>
						<p class="mt-2 text-sm text-surface-600-400">
							Progreso: {lineStatus.lote.piezasOk} OK / {lineStatus.lote.piezasFallas} NOK
						</p>
					</div>
				{/if}
			</section>

			<!-- Modal Footer -->
			<footer class="card-footer flex gap-3 bg-surface-200-800 p-6">
				<button
					class="variant-ghost-surface btn min-h-[60px] flex-1 touch-manipulation px-6 py-4 text-lg"
					onclick={closeStopProductionModal}
				>
					<IconX size={24} />
					<span>Cancelar</span>
				</button>
				<button
					class="variant-filled-error btn min-h-[60px] flex-1 touch-manipulation px-6 py-4 text-lg"
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
