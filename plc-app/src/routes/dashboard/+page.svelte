<script lang="ts">
	import { format } from 'date-fns';
	import { es } from 'date-fns/locale';
	import IconFactory from '@lucide/svelte/icons/factory';
	import IconPackage from '@lucide/svelte/icons/package';
	import IconCheckCircle from '@lucide/svelte/icons/check-circle';
	import IconXCircle from '@lucide/svelte/icons/x-circle';
	import IconActivity from '@lucide/svelte/icons/activity';
	import IconTrendingUp from '@lucide/svelte/icons/trending-up';
	import IconClipboardList from '@lucide/svelte/icons/clipboard-list';
	import IconClock from '@lucide/svelte/icons/clock';
	import IconUser from '@lucide/svelte/icons/user';
	import IconArrowRight from '@lucide/svelte/icons/arrow-right';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const user = $derived(data?.user);
	const stats = $derived(data?.stats);
	const ultimosLotes = $derived(data?.ultimosLotes || []);

	// Determinar el saludo según la hora
	const getGreeting = () => {
		const hour = new Date().getHours();
		if (hour < 12) return 'Buenos días';
		if (hour < 18) return 'Buenas tardes';
		return 'Buenas noches';
	};

	const greeting = getGreeting();

	// Función para obtener el badge del estado del lote
	const getEstadoBadge = (estado: string) => {
		switch (estado) {
			case 'OPEN':
				return 'variant-filled-success';
			case 'PAUSED':
				return 'variant-filled-warning';
			case 'CLOSED':
				return 'variant-filled-surface';
			default:
				return 'variant-filled-surface';
		}
	};
</script>

<div class="dashboard-home h-full overflow-auto p-6 space-y-6">
	<!-- Header de Bienvenida -->
	<header class="space-y-2">
		<div class="flex items-center gap-4">
			<div class="rounded-full bg-primary-500/10 p-3">
				<IconFactory size={32} class="text-primary-500" />
			</div>
			<div>
				<h1 class="h2 font-bold">
					{greeting}, {user?.username || 'Usuario'}!
				</h1>
				<p class="text-surface-600-400">Sistema de Control de Calidad Industrial</p>
			</div>
		</div>
	</header>

	<!-- Estadísticas Generales -->
	<section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
		<!-- Total de Recetas -->
		<div class="card variant-glass-surface p-6 space-y-3 hover:variant-soft-primary transition-all">
			<div class="flex items-center justify-between">
				<div class="rounded-full bg-primary-500/10 p-3">
					<IconClipboardList size={24} class="text-primary-500" />
				</div>
				<span class="text-3xl font-bold">{stats?.totalRecetas || 0}</span>
			</div>
			<div>
				<p class="text-sm text-surface-600-400">Recetas Activas</p>
				<p class="text-xs text-surface-500-400 mt-1">Modelos configurados</p>
			</div>
		</div>

		<!-- Lotes Activos -->
		<div class="card variant-glass-surface p-6 space-y-3 hover:variant-soft-warning transition-all">
			<div class="flex items-center justify-between">
				<div class="rounded-full bg-warning-500/10 p-3">
					<IconActivity size={24} class="text-warning-500" />
				</div>
				<span class="text-3xl font-bold">{stats?.lotesActivos || 0}</span>
			</div>
			<div>
				<p class="text-sm text-surface-600-400">Lotes Activos</p>
				<p class="text-xs text-surface-500-400 mt-1">En producción</p>
			</div>
		</div>

		<!-- Piezas OK -->
		<div class="card variant-glass-surface p-6 space-y-3 hover:variant-soft-success transition-all">
			<div class="flex items-center justify-between">
				<div class="rounded-full bg-success-500/10 p-3">
					<IconCheckCircle size={24} class="text-success-500" />
				</div>
				<span class="text-3xl font-bold text-success-500">{stats?.totalPiezasOK || 0}</span>
			</div>
			<div>
				<p class="text-sm text-surface-600-400">Piezas Aprobadas</p>
				<p class="text-xs text-success-500 mt-1 flex items-center gap-1">
					<IconTrendingUp size={14} />
					{stats?.precisión || '0.0'}% Precisión
				</p>
			</div>
		</div>

		<!-- Piezas NOK -->
		<div class="card variant-glass-surface p-6 space-y-3 hover:variant-soft-error transition-all">
			<div class="flex items-center justify-between">
				<div class="rounded-full bg-error-500/10 p-3">
					<IconXCircle size={24} class="text-error-500" />
				</div>
				<span class="text-3xl font-bold text-error-500">{stats?.totalPiezasNOK || 0}</span>
			</div>
			<div>
				<p class="text-sm text-surface-600-400">Piezas Rechazadas</p>
				<p class="text-xs text-surface-500-400 mt-1">Defectos detectados</p>
			</div>
		</div>
	</section>

	<!-- Resumen de Producción -->
	<section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Tarjeta de Producción Total -->
		<div class="card variant-glass-surface p-6 space-y-4">
			<div class="flex items-center gap-3">
				<div class="rounded-full bg-primary-500/10 p-3">
					<IconPackage size={28} class="text-primary-500" />
				</div>
				<div>
					<p class="text-sm text-surface-600-400">Producción Total</p>
					<p class="text-2xl font-bold">{stats?.totalPiezas || 0}</p>
				</div>
			</div>
			<div class="space-y-2">
				<div class="flex justify-between text-sm">
					<span class="text-surface-600-400">Piezas OK</span>
					<span class="font-semibold text-success-500">{stats?.totalPiezasOK || 0}</span>
				</div>
				<div class="flex justify-between text-sm">
					<span class="text-surface-600-400">Piezas NOK</span>
					<span class="font-semibold text-error-500">{stats?.totalPiezasNOK || 0}</span>
				</div>
				<div class="h-2 bg-surface-200-800 rounded-full overflow-hidden">
					<div 
						class="h-full bg-success-500 transition-all duration-500"
						style="width: {stats?.precisión || 0}%"
					></div>
				</div>
				<p class="text-xs text-center text-surface-500-400">
					Tasa de Aprobación: {stats?.precisión || '0.0'}%
				</p>
			</div>
		</div>

		<!-- Tarjeta de Lotes -->
		<div class="card variant-glass-surface p-6 space-y-4">
			<div class="flex items-center gap-3">
				<div class="rounded-full bg-warning-500/10 p-3">
					<IconClipboardList size={28} class="text-warning-500" />
				</div>
				<div>
					<p class="text-sm text-surface-600-400">Estado de Lotes</p>
					<p class="text-2xl font-bold">{stats?.totalLotes || 0}</p>
				</div>
			</div>
			<div class="space-y-2">
				<div class="flex justify-between text-sm">
					<span class="text-surface-600-400">Activos</span>
					<span class="font-semibold text-warning-500">{stats?.lotesActivos || 0}</span>
				</div>
				<div class="flex justify-between text-sm">
					<span class="text-surface-600-400">Cerrados</span>
					<span class="font-semibold">{(stats?.totalLotes || 0) - (stats?.lotesActivos || 0)}</span>
				</div>
			</div>
		</div>

		<!-- Accesos Rápidos -->
		
	</section>

	<!-- Últimos Lotes -->
	{#if ultimosLotes.length > 0}
		<section class="card variant-glass-surface p-6 space-y-4">
			<div class="flex items-center justify-between">
				<h2 class="h3 font-bold flex items-center gap-2">
					<IconClock size={24} />
					Últimos Lotes Procesados
				</h2>
				<a href="/dashboard/history" class="btn variant-soft-primary btn-sm">
					Ver Todos
					<IconArrowRight size={16} />
				</a>
			</div>

			<div class="table-container">
				<table class="table table-hover">
					<thead>
						<tr>
							<th>Lote</th>
							<th>Receta (PPN)</th>
							<th>Estado</th>
							<th>Piezas OK</th>
							<th>Piezas NOK</th>
							<th>Creador</th>
							<th>Fecha</th>
						</tr>
					</thead>
					<tbody>
						{#each ultimosLotes as lote}
							<tr>
								<td class="font-semibold">{lote.name}</td>
								<td>
									<div class="flex flex-col">
										<span class="font-medium">{lote.receta.ppn}</span>
										<span class="text-xs text-surface-500-400 truncate max-w-xs">
											{lote.receta.item_description}
										</span>
									</div>
								</td>
								<td>
									<span class="badge {getEstadoBadge(lote.estado)} text-xs">
										{lote.estado}
									</span>
								</td>
								<td>
									<span class="flex items-center gap-1 text-success-500 font-semibold">
										<IconCheckCircle size={16} />
										{lote.piezas_ok}
									</span>
								</td>
								<td>
									<span class="flex items-center gap-1 text-error-500 font-semibold">
										<IconXCircle size={16} />
										{lote.piezas_fallas}
									</span>
								</td>
								<td>
									<span class="flex items-center gap-1">
										<IconUser size={14} class="text-surface-500-400" />
										{lote.creator.username}
									</span>
								</td>
								<td class="text-sm text-surface-600-400">
									{format(new Date(lote.started_at), 'dd/MM/yyyy HH:mm', { locale: es })}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</section>
	{:else}
		<section class="card variant-glass-surface p-12 text-center">
			<div class="flex flex-col items-center gap-4">
				<div class="rounded-full bg-surface-200-800 p-8">
					<IconPackage size={48} class="text-surface-400-600" />
				</div>
				<div>
					<h3 class="h3 font-bold mb-2">No hay lotes registrados</h3>
					<p class="text-surface-600-400">
						Comienza creando un nuevo lote en la sección de Gestión
					</p>
				</div>
				<a href="/dashboard/management/lotes" class="btn variant-filled-primary mt-4">
					<IconClipboardList size={20} />
					<span>Crear Lote</span>
				</a>
			</div>
		</section>
	{/if}

	<!-- Footer Info -->
	<footer class="text-center py-4 text-sm text-surface-500-400">
		<p>Sistema de Trazabilidad y Control de Calidad Industrial - AxmeTech © 2025</p>
	</footer>
</div>

<style>
	.dashboard-home {
		animation: fadeIn 0.3s ease-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Truncate text */
	.truncate {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
</style>
