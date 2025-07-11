<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	function navigateToLogin() {
		goto('/login');
	}

	// Lista de diagramas disponibles
	const diagramas = [
		{ name: '1-Arquitectura', title: 'Arquitectura del Sistema', description: 'Diagrama completo de la arquitectura del sistema' },
		{ name: '2-Entidad-Relacion', title: 'Esquema de Base de Datos', description: 'Diseño de entidades y relaciones de la base de datos' },
		{ name: '3-Flujo-data', title: 'Flujo de Datos', description: 'Flujo de datos entre componentes del sistema' },
		{ name: '4-mapeo-modbus', title: 'Mapeo Modbus', description: 'Configuración del protocolo Modbus TCP' },
		{ name: '5-endpoints', title: 'Endpoints API', description: 'Documentación de endpoints REST disponibles' },
		{ name: '6-frontend', title: 'Estructura Frontend', description: 'Arquitectura y componentes del frontend' },
		{ name: '7-roles', title: 'Roles y Autenticación', description: 'Sistema de roles y control de acceso' },
		{ name: '8-despliegue', title: 'Despliegue del Sistema', description: 'Arquitectura de despliegue en servidor' }
	];

	// Tipos
	type Diagrama = typeof diagramas[0];

	// Estado del modal
	let modalOpen = false;
	let currentDiagram: Diagrama | null = null;
	let currentDiagramIndex = 0;
	let modalElement: HTMLDivElement | null = null;

	// Estado del zoom y pan
	let scale = 1;
	let translateX = 0;
	let translateY = 0;
	let isDragging = false;
	let lastMouseX = 0;
	let lastMouseY = 0;

	// Estado de pantalla completa
	let isFullscreen = false;

	// Funciones del modal
	function openModal(diagrama: Diagrama, index: number) {
		currentDiagram = diagrama;
		currentDiagramIndex = index;
		modalOpen = true;
		resetZoom();
		// Prevenir scroll del body
		document.body.style.overflow = 'hidden';
	}

	function closeModal() {
		// Salir de fullscreen si está activo
		if (isFullscreen) {
			exitFullscreen();
		}
		modalOpen = false;
		currentDiagram = null;
		// Restaurar scroll del body
		document.body.style.overflow = 'auto';
	}

	function nextDiagram() {
		if (currentDiagramIndex < diagramas.length - 1) {
			currentDiagramIndex++;
			currentDiagram = diagramas[currentDiagramIndex];
			resetZoom();
		}
	}

	function prevDiagram() {
		if (currentDiagramIndex > 0) {
			currentDiagramIndex--;
			currentDiagram = diagramas[currentDiagramIndex];
			resetZoom();
		}
	}

	// Funciones de zoom y pan
	function zoomIn() {
		scale = Math.min(scale * 1.3, 5);
	}

	function zoomOut() {
		scale = Math.max(scale / 1.3, 0.5);
	}

	function resetZoom() {
		scale = 1;
		translateX = 0;
		translateY = 0;
	}

	function handleWheel(event: WheelEvent) {
		event.preventDefault();
		const delta = event.deltaY > 0 ? 0.9 : 1.1;
		scale = Math.max(0.5, Math.min(5, scale * delta));
	}

	function handleMouseDown(event: MouseEvent) {
		if (event.button === 0) { // Solo botón izquierdo
			isDragging = true;
			lastMouseX = event.clientX;
			lastMouseY = event.clientY;
		}
	}

	function handleMouseMove(event: MouseEvent) {
		if (isDragging) {
			const deltaX = event.clientX - lastMouseX;
			const deltaY = event.clientY - lastMouseY;
			translateX += deltaX;
			translateY += deltaY;
			lastMouseX = event.clientX;
			lastMouseY = event.clientY;
		}
	}

	function handleMouseUp() {
		isDragging = false;
	}

	// Funciones de pantalla completa
	function toggleFullscreen() {
		if (isFullscreen) {
			exitFullscreen();
		} else {
			enterFullscreen();
		}
	}

	function enterFullscreen() {
		if (modalElement && modalElement.requestFullscreen) {
			modalElement.requestFullscreen();
		} else if (modalElement && (modalElement as any).webkitRequestFullscreen) {
			(modalElement as any).webkitRequestFullscreen();
		} else if (modalElement && (modalElement as any).msRequestFullscreen) {
			(modalElement as any).msRequestFullscreen();
		}
	}

	function exitFullscreen() {
		if (document.exitFullscreen) {
			document.exitFullscreen();
		} else if ((document as any).webkitExitFullscreen) {
			(document as any).webkitExitFullscreen();
		} else if ((document as any).msExitFullscreen) {
			(document as any).msExitFullscreen();
		}
	}

	function handleFullscreenChange() {
		isFullscreen = !!(
			document.fullscreenElement ||
			(document as any).webkitFullscreenElement ||
			(document as any).msFullscreenElement
		);
	}

	// Manejar teclas de escape
	function handleKeydown(event: KeyboardEvent) {
		if (modalOpen) {
			switch(event.key) {
				case 'Escape':
					closeModal();
					break;
				case 'ArrowLeft':
					prevDiagram();
					break;
				case 'ArrowRight':
					nextDiagram();
					break;
				case '+':
				case '=':
					zoomIn();
					break;
				case '-':
					zoomOut();
					break;
				case '0':
					resetZoom();
					break;
				case 'f':
				case 'F':
					toggleFullscreen();
					break;
			}
		}
	}

	onMount(() => {
		// Escuchar cambios de pantalla completa
		document.addEventListener('fullscreenchange', handleFullscreenChange);
		document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
		document.addEventListener('msfullscreenchange', handleFullscreenChange);

		return () => {
			document.removeEventListener('fullscreenchange', handleFullscreenChange);
			document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
			document.removeEventListener('msfullscreenchange', handleFullscreenChange);
		};
	});
</script>

<svelte:window on:keydown={handleKeydown} on:mouseup={handleMouseUp} on:mousemove={handleMouseMove} />

<svelte:head>
	<title>AXME - Sistema de Producción Industrial</title>
	<meta name="description" content="Sistema integral de monitoreo y control de producción industrial con protocolo Modbus TCP" />
	<style>
		/* Permitir scroll solo en esta página */
		html, body {
			overflow: auto !important;
		}
		
		/* Estilos optimizados para la galería de diagramas */
		.diagram-container {
			transition: transform 0.2s ease;
			will-change: transform;
		}
		
		.diagram-container:hover {
			transform: translateY(-2px);
		}
		
		/* Optimización de imágenes */
		.diagram-image {
			transition: transform 0.2s ease;
			will-change: transform;
		}
		
		.diagram-image:hover {
			transform: scale(1.02);
		}

		/* Estilos del modal */
		.modal-backdrop {
			backdrop-filter: blur(8px);
			animation: fadeIn 0.3s ease-out;
		}

		.modal-content {
			animation: slideIn 0.3s ease-out;
		}

		.modal-content:fullscreen {
			border-radius: 0;
			max-width: 100vw;
			max-height: 100vh;
			width: 100vw;
			height: 100vh;
		}

		.modal-diagram {
			cursor: grab;
			transition: transform 0.1s ease-out;
		}

		.modal-diagram:active {
			cursor: grabbing;
		}

		@keyframes fadeIn {
			from { opacity: 0; }
			to { opacity: 1; }
		}

		@keyframes slideIn {
			from { 
				opacity: 0;
				transform: scale(0.9) translateY(20px);
			}
			to { 
				opacity: 1;
				transform: scale(1) translateY(0);
			}
		}

		/* Botones del modal */
		.modal-button {
			backdrop-filter: blur(10px);
			transition: all 0.2s ease;
		}

		.modal-button:hover {
			transform: scale(1.1);
		}

		/* Placeholder para casos de carga lenta */
		.diagram-placeholder {
			background: linear-gradient(90deg, rgba(255,255,255,0.1) 25%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.1) 75%);
			background-size: 200% 100%;
			animation: shimmer 1.5s infinite;
		}
		
		@keyframes shimmer {
			0% { background-position: -200% 0; }
			100% { background-position: 200% 0; }
		}
	</style>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-[#17191c] via-[#1e2024] to-[#0e3c61]">
	<!-- Hero Section -->
	<div class="relative overflow-hidden">
		<!-- Background Pattern -->
		<div class="absolute inset-0 opacity-10">
			<div class="absolute inset-0" style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0); background-size: 50px 50px;"></div>
		</div>
		
		<div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
			<!-- Main Content -->
			<div class="text-center">
				<!-- Logo/Title -->
				<div class="mb-8">
					<h1 class="text-6xl lg:text-8xl font-bold text-white mb-4 tracking-tight">
						<span class="bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
							AXME
						</span>
					</h1>
					<p class="text-xl lg:text-2xl text-blue-200 font-light">
						Sistema de Producción Industrial
					</p>
				</div>

				<!-- Subtitle -->
				<div class="max-w-3xl mx-auto mb-12">
					<p class="text-lg lg:text-xl text-gray-300 leading-relaxed">
						Sistema integral de monitoreo y control de producción industrial que integra equipos PLC mediante 
						<span class="text-blue-300 font-semibold">protocolo Modbus TCP</span>, 
						proporcionando visualización en tiempo real, análisis histórico y gestión de calidad.
					</p>
				</div>

				<!-- Key Features Grid -->
				<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
					<div class="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all duration-300">
						<div class="text-4xl mb-4">📡</div>
						<h3 class="text-lg font-semibold text-white mb-2">Comunicación Industrial</h3>
						<p class="text-sm text-gray-400">Protocolo Modbus TCP para integración con PLCs</p>
					</div>

					<div class="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all duration-300">
						<div class="text-4xl mb-4">⏱️</div>
						<h3 class="text-lg font-semibold text-white mb-2">Tiempo Real</h3>
						<p class="text-sm text-gray-400">Dashboard con datos en vivo mediante WebSockets</p>
					</div>

					<div class="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all duration-300">
						<div class="text-4xl mb-4">🎯</div>
						<h3 class="text-lg font-semibold text-white mb-2">Control de Calidad</h3>
						<p class="text-sm text-gray-400">Inspección visual con 2-3 cámaras por modelo</p>
					</div>

					<div class="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all duration-300">
						<div class="text-4xl mb-4">📊</div>
						<h3 class="text-lg font-semibold text-white mb-2">Análisis Histórico</h3>
						<p class="text-sm text-gray-400">Reportes detallados y análisis de tendencias</p>
					</div>
				</div>

				<!-- Benefits Section -->
				<div class="bg-white/5 backdrop-blur-sm rounded-2xl p-8 mb-12 border border-white/10">
					<h2 class="text-2xl font-bold text-white mb-6">Beneficios Clave</h2>
					<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 text-left">
						<div class="flex items-start space-x-3">
							<div class="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
							<div>
								<h4 class="text-white font-semibold">Visibilidad Total</h4>
								<p class="text-gray-400 text-sm">Monitoreo 24/7 de líneas de producción</p>
							</div>
						</div>
						
						<div class="flex items-start space-x-3">
							<div class="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
							<div>
								<h4 class="text-white font-semibold">Calidad Asegurada</h4>
								<p class="text-gray-400 text-sm">Detección automática de defectos</p>
							</div>
						</div>
						
						<div class="flex items-start space-x-3">
							<div class="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
							<div>
								<h4 class="text-white font-semibold">Trazabilidad Completa</h4>
								<p class="text-gray-400 text-sm">Registro de todas las operaciones</p>
							</div>
						</div>
						
						<div class="flex items-start space-x-3">
							<div class="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
							<div>
								<h4 class="text-white font-semibold">Escalabilidad</h4>
								<p class="text-gray-400 text-sm">Arquitectura preparada para crecimiento</p>
							</div>
						</div>
						
						<div class="flex items-start space-x-3">
							<div class="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
							<div>
								<h4 class="text-white font-semibold">Integración</h4>
								<p class="text-gray-400 text-sm">Compatible con sistemas existentes</p>
							</div>
						</div>
						
						<div class="flex items-start space-x-3">
							<div class="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
							<div>
								<h4 class="text-white font-semibold">Seguridad</h4>
								<p class="text-gray-400 text-sm">Autenticación JWT con 4 niveles de acceso</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Architecture Highlight -->
				<div class="bg-gradient-to-r from-[#0e3c61]/20 to-[#17191c]/20 rounded-2xl p-8 mb-12 border border-blue-500/20">
					<h2 class="text-2xl font-bold text-white mb-4">Arquitectura Optimizada</h2>
					<p class="text-gray-300 mb-6">
						Desplegado en servidor único para máxima simplicidad y confiabilidad operativa
					</p>
					<div class="grid md:grid-cols-3 gap-6 text-sm">
						<div class="text-center">
							<div class="text-3xl mb-2">🏭</div>
							<h4 class="text-white font-semibold">PLC Externo</h4>
							<p class="text-gray-400">192.168.1.100</p>
						</div>
						<div class="text-center">
							<div class="text-3xl mb-2">🖥️</div>
							<h4 class="text-white font-semibold">Servidor Principal</h4>
							<p class="text-gray-400">192.168.1.200</p>
						</div>
						<div class="text-center">
							<div class="text-3xl mb-2">👥</div>
							<h4 class="text-white font-semibold">Usuarios Finales</h4>
							<p class="text-gray-400">Múltiples dispositivos</p>
						</div>
					</div>
				</div>

				<!-- CTA Button -->
				<div class="space-y-4 mb-16">
					<button 
						on:click={navigateToLogin}
						class="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
					>
						<span class="mr-2">🚀</span>
						Acceder al Sistema
					</button>
					<p class="text-sm text-gray-400">
						Inicia sesión para acceder al dashboard de monitoreo en tiempo real
					</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Diagramas Técnicos Section -->
	<section class="relative py-20 bg-black/20 backdrop-blur-sm border-t border-white/10">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center mb-16">
				<h2 class="text-4xl font-bold text-white mb-4">📋 Documentación Técnica</h2>
				<p class="text-xl text-gray-300 max-w-3xl mx-auto">
					Explora en detalle la arquitectura, flujos de datos, y componentes del sistema AXME a través de nuestros diagramas técnicos interactivos.
				</p>
			</div>

			<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
				{#each diagramas as diagrama, index}
				<div class="diagram-container bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 cursor-pointer group">
					<div class="aspect-square mb-4 bg-white/10 rounded-lg overflow-hidden">
						<img 
							src="/diagramas/{diagrama.name}.svg" 
							alt={diagrama.title}
							class="diagram-image w-full h-full object-contain p-2"
							loading="eager"
							decoding="async"
							fetchpriority="high"
						/>
					</div>
					<h3 class="text-lg font-semibold text-white mb-2 group-hover:text-blue-300 transition-colors">
						{diagrama.title}
					</h3>
					<p class="text-sm text-gray-400 mb-4">
						{diagrama.description}
					</p>
					<button 
						class="w-full py-2 px-4 bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 rounded-lg transition-all duration-200 text-sm font-medium"
						on:click={() => openModal(diagrama, index)}
					>
						Ver Diagrama Completo
					</button>
				</div>
				{/each}
			</div>

			<!-- Información adicional sobre los diagramas -->
			<div class="mt-16 bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
				<h3 class="text-2xl font-bold text-white mb-6 text-center">🔍 Guía de Diagramas</h3>
				<div class="grid md:grid-cols-2 gap-8 text-sm">
					<div>
						<h4 class="text-lg font-semibold text-white mb-3">Arquitectura y Diseño</h4>
						<ul class="space-y-2 text-gray-300">
							<li class="flex items-start space-x-2">
								<span class="text-blue-400">•</span>
								<span><strong>Arquitectura:</strong> Vista general del sistema completo</span>
							</li>
							<li class="flex items-start space-x-2">
								<span class="text-blue-400">•</span>
								<span><strong>Base de Datos:</strong> Esquema entidad-relación detallado</span>
							</li>
							<li class="flex items-start space-x-2">
								<span class="text-blue-400">•</span>
								<span><strong>Frontend:</strong> Estructura de componentes y rutas</span>
							</li>
							<li class="flex items-start space-x-2">
								<span class="text-blue-400">•</span>
								<span><strong>Despliegue:</strong> Configuración del servidor</span>
							</li>
						</ul>
					</div>
					<div>
						<h4 class="text-lg font-semibold text-white mb-3">Funcionalidad y Flujos</h4>
						<ul class="space-y-2 text-gray-300">
							<li class="flex items-start space-x-2">
								<span class="text-blue-400">•</span>
								<span><strong>Flujo de Datos:</strong> Procesamiento en tiempo real</span>
							</li>
							<li class="flex items-start space-x-2">
								<span class="text-blue-400">•</span>
								<span><strong>Modbus:</strong> Mapeo de direcciones y protocolos</span>
							</li>
							<li class="flex items-start space-x-2">
								<span class="text-blue-400">•</span>
								<span><strong>API Endpoints:</strong> Servicios REST disponibles</span>
							</li>
							<li class="flex items-start space-x-2">
								<span class="text-blue-400">•</span>
								<span><strong>Roles:</strong> Sistema de autenticación y permisos</span>
							</li>
						</ul>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Footer -->
	<footer class="bg-black/20 backdrop-blur-sm border-t border-white/10 py-8">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
			<p class="text-gray-400 text-sm">
				© 2024 AXME - Sistema de Producción Industrial. Tecnología avanzada para la industria 4.0
			</p>
		</div>
	</footer>
</div>

<!-- Modal para visualizar diagramas -->
{#if modalOpen && currentDiagram}
<div 
	class="modal-backdrop fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
	on:click={closeModal}
>
	<div 
		bind:this={modalElement}
		class="modal-content relative w-full h-full max-w-7xl max-h-full bg-[#1a1d21] rounded-2xl border border-white/20 overflow-hidden"
		on:click|stopPropagation
	>
		<!-- Header del modal -->
		<div class="absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-[#1a1d21] to-transparent p-6">
			<div class="flex items-center justify-between">
				<div>
					<h3 class="text-2xl font-bold text-white">{currentDiagram.title}</h3>
					<p class="text-gray-400 text-sm">{currentDiagram.description}</p>
				</div>
				<div class="flex items-center space-x-2">
					<!-- Botón de pantalla completa -->
					<button 
						class="modal-button text-white bg-blue-500/20 hover:bg-blue-500/40 p-3 rounded-full"
						on:click={toggleFullscreen}
						title="{isFullscreen ? 'Salir de pantalla completa (F)' : 'Pantalla completa (F)'}"
					>
						{#if isFullscreen}
							<!-- Icono: Salir de pantalla completa -->
							<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M15 9V4.5M15 9h4.5M15 9l5.25-5.25M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 15v4.5M15 15h4.5m0 0l5.25 5.25"></path>
							</svg>
						{:else}
							<!-- Icono: Entrar a pantalla completa -->
							<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15"></path>
							</svg>
						{/if}
					</button>
					<!-- Botón de cerrar -->
					<button 
						class="modal-button text-white bg-red-500/20 hover:bg-red-500/40 p-3 rounded-full"
						on:click={closeModal}
						title="Cerrar (Esc)"
					>
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
						</svg>
					</button>
				</div>
			</div>
		</div>

		<!-- Área del diagrama -->
		<div 
			class="w-full h-full flex items-center justify-center pt-24 pb-20 overflow-hidden"
			on:wheel={handleWheel}
			on:mousedown={handleMouseDown}
		>
			<img 
				src="/diagramas/{currentDiagram.name}.svg" 
				alt={currentDiagram.title}
				class="modal-diagram max-w-none select-none"
				style="transform: scale({scale}) translate({translateX}px, {translateY}px);"
				draggable="false"
			/>
		</div>

		<!-- Controles del modal -->
		<div class="absolute bottom-0 left-0 right-0 z-10 bg-gradient-to-t from-[#1a1d21] to-transparent p-6">
			<div class="flex items-center justify-between">
				<!-- Navegación de diagramas -->
				<div class="flex items-center space-x-2">
					<button 
						class="modal-button text-white bg-white/10 hover:bg-white/20 p-3 rounded-full disabled:opacity-50 disabled:cursor-not-allowed"
						on:click={prevDiagram}
						disabled={currentDiagramIndex === 0}
						title="Anterior (←)"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
						</svg>
					</button>
					<span class="text-white text-sm px-3">{currentDiagramIndex + 1} / {diagramas.length}</span>
					<button 
						class="modal-button text-white bg-white/10 hover:bg-white/20 p-3 rounded-full disabled:opacity-50 disabled:cursor-not-allowed"
						on:click={nextDiagram}
						disabled={currentDiagramIndex === diagramas.length - 1}
						title="Siguiente (→)"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
						</svg>
					</button>
				</div>

				<!-- Controles de zoom -->
				<div class="flex items-center space-x-2">
					<button 
						class="modal-button text-white bg-white/10 hover:bg-white/20 p-3 rounded-full"
						on:click={zoomOut}
						title="Alejar (-)"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
						</svg>
					</button>
					<span class="text-white text-sm px-3 w-16 text-center">{Math.round(scale * 100)}%</span>
					<button 
						class="modal-button text-white bg-white/10 hover:bg-white/20 p-3 rounded-full"
						on:click={zoomIn}
						title="Acercar (+)"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
						</svg>
					</button>
					<button 
						class="modal-button text-white bg-blue-500/20 hover:bg-blue-500/40 p-3 rounded-full"
						on:click={resetZoom}
						title="Restablecer (0)"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
						</svg>
					</button>
				</div>

				<!-- Información de ayuda -->
				<div class="text-xs text-gray-400 text-center">
					<div>🖱️ Rueda: Zoom | Arrastrar: Mover</div>
					<div>⌨️ ←→: Navegar | +/-: Zoom | 0: Reset | F: Fullscreen | Esc: Cerrar</div>
				</div>
			</div>
		</div>
	</div>
</div>
{/if}

