<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<main
	class="flex min-h-screen items-center justify-center bg-gradient-to-br from-surface-50 to-surface-200 p-4 dark:from-surface-900 dark:to-surface-950"
>
	<!-- Background Pattern -->
	<div class="absolute inset-0 opacity-5">
		<div
			class="absolute inset-0"
			style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.3) 1px, transparent 0); background-size: 20px 20px;"
		></div>
	</div>

	<div class="container mx-auto">
		{#if children}
			{@render children?.()}
		{:else}
			<p class="text-center text-gray-500">No content available.</p>
		{/if}
	</div>
</main>
