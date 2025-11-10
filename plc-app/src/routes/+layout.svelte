<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<main class="grid h-screen w-screen grid-cols-[auto_1fr] overflow-hidden">
	{#if children}
		{@render children?.()}
	{/if}
</main>
