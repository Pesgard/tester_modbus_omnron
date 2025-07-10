<script lang="ts">
	import { Navigation } from '@skeletonlabs/skeleton-svelte';
	// Icons
	import IconHome from '@lucide/svelte/icons/home';
	import IconHistory from '@lucide/svelte/icons/history';
	import IconLogOut from '@lucide/svelte/icons/log-out';
	import IconUser from '@lucide/svelte/icons/user';
	// State
	let value = $state('home');

	let userRole = $state('Operator');

	let { children } = $props();
</script>

<div class="h-screen w-screen grid grid-cols-[auto_1fr] overflow-hidden">
	<!-- Navigation Rail - Fixed -->
	<div class="card border-surface-100-900 border-r-[1px] h-full dashboard-rail">
		<Navigation.Rail {value} onValueChange={(newValue) => (value = newValue)}>
			{#snippet header()}
			<!-- Show user role , not Selectable only admin can select -->
			<Navigation.Tile label={userRole} selected={false}><IconUser /></Navigation.Tile>
			{/snippet}
			{#snippet tiles()}
			<Navigation.Tile id="home" label="Production" href="/home"><IconHome /></Navigation.Tile>
			<Navigation.Tile id="history" label="History" href="/history"><IconHistory /></Navigation.Tile>
			<Navigation.Tile id="managment" label="Management" href="/managment"><IconUser /></Navigation.Tile>
			{/snippet}
			{#snippet footer()}
			<Navigation.Tile id="logout" label="Log out" href="/login"><IconLogOut /></Navigation.Tile>
			{/snippet}
		</Navigation.Rail>
	</div>

	<!-- Content Area - Scrollable -->
	<div class="dashboard-content custom-scroll bg-surface-50-950">
		{@render children()}
	</div>
</div>