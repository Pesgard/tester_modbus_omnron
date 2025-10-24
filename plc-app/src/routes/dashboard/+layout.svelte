<script lang="ts">
	import Sidebar from "$lib/components/sidebar/Sidebar.svelte";

	let { data, children } = $props();
	// $inspect(data);

	const user = $derived(data.user);
	// Usuario con roles y permisos disponible en todas las páginas del dashboard
</script>

<!-- Layout del dashboard - todas las subrutas se renderizan aquí -->
<div class="h-screen w-screen grid grid-cols-[auto_1fr] overflow-hidden">	<!-- Header o navegación global del dashboard puede ir aquí -->
	{#if user}
		<Sidebar {user} />
	{/if}
	<!-- Contenido de las páginas hijas -->
	{@render children()}
</div>

