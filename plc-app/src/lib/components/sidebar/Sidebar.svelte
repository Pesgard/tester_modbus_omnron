<script lang="ts">
	import { Navigation } from '@skeletonlabs/skeleton-svelte';
	import { goto } from '$app/navigation';
	// Icons
	import IconLogOut from '@lucide/svelte/icons/log-out';
	import IconUser from '@lucide/svelte/icons/user';

	// Navigation sections
	import { navSections } from './navigationSections';

	// Props
	interface Props {
		user: {
			id: string;
			username: string;
			roles: string[];
			permisos: string[];
		};
	}

	const { user }: Props = $props();

	// State
	let value = $state('production');
	const userName = user.username;
	let isLoggingOut = $state(false);

	/**
	 * Verifica si el usuario tiene un permiso específico
	 * Soporta wildcards: *, namespace.*
	 */
	const hasPermission = (permission: string): boolean => {
		if (!user || !user.permisos) return false;

		// Admin global
		if (user.permisos.includes('*')) return true;

		// Coincidencia exacta
		if (user.permisos.includes(permission)) return true;

		// Wildcard por namespace (ej: lote.* permite lote.ver)
		const [namespace] = permission.split('.');
		if (user.permisos.includes(`${namespace}.*`)) return true;

		return false;
	};

	/**
	 * Maneja el cierre de sesión usando el endpoint API
	 */
	const handleLogout = async () => {
		if (isLoggingOut) return;
		
		isLoggingOut = true;
		
		try {
			const response = await fetch('/api/auth/logout', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				// Redirigir al login después de cerrar sesión exitosamente
				await goto('/login', { replaceState: true, invalidateAll: true });
			} else {
				console.error('Error al cerrar sesión');
				// Intentar redirigir de todas formas
				await goto('/login', { replaceState: true, invalidateAll: true });
			}
		} catch (error) {
			console.error('Error al cerrar sesión:', error);
			// Intentar redirigir de todas formas
			await goto('/login', { replaceState: true, invalidateAll: true });
		} finally {
			isLoggingOut = false;
		}
	};

	// Filtrar secciones según permisos del usuario
	const visibleSections = $derived(
		navSections.filter((section) => hasPermission(section.permission))
	);
</script>

<div class="dashboard-rail h-full card border-r-[1px] border-surface-100-900">
	<Navigation.Rail {value} onValueChange={(newValue) => (value = newValue)}>
		{#snippet header()}
			<!-- Show user role , not Selectable only admin can select -->
			<Navigation.Tile label={userName} selected={false}><IconUser /></Navigation.Tile>
		{/snippet}
		{#snippet tiles()}
			<!-- Renderizar solo las secciones visibles según permisos -->
			{#each visibleSections as section}
				{@const Icon = section.icon}
				<Navigation.Tile id={section.id} label={section.label} href={section.href}>
					<Icon />
				</Navigation.Tile>
			{/each}

			<!-- Settings siempre visible
			<Navigation.Tile id="settings" label="Settings" href="/dashboard/settings">
				<IconSettings />
			</Navigation.Tile> -->
		{/snippet}
		{#snippet footer()}
			<button
				type="button"
				onclick={handleLogout}
				disabled={isLoggingOut}
				class="w-full"
				aria-label="Cerrar sesión"
			>
				<Navigation.Tile id="logout" label={isLoggingOut ? 'Cerrando...' : 'Log out'}>
					<IconLogOut class={isLoggingOut ? 'animate-pulse' : ''} />
				</Navigation.Tile>
			</button>
		{/snippet}
	</Navigation.Rail>
</div>
