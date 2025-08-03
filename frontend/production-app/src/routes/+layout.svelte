<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { getWebSocketInstance } from '$lib/services/websocket';

	interface Props {
		children: any;
	}

	let { children }: Props = $props();

	// Initialize auth from localStorage
	onMount(() => {
		authStore.initializeFromStorage();
		
		// Connect WebSocket if authenticated
		const unsubscribe = authStore.subscribe((auth) => {
			if (auth.isAuthenticated) {
				const ws = getWebSocketInstance();
				ws.connect();
			}
		});

		return () => {
			unsubscribe();
			// Disconnect WebSocket on component destroy
			const ws = getWebSocketInstance();
			ws.disconnect();
		};
	});

	// Navigation items
	const navItems = [
		{ 
			label: 'Dashboard', 
			href: '/', 
			icon: '📊'
		},
		{ 
			label: 'Production History', 
			href: '/history', 
			icon: '📈'
		},
		{ 
			label: 'Admin Panel', 
			href: '/admin', 
			icon: '⚙️',
			requireRole: 'admin'
		}
	];

	function handleLogout() {
		const ws = getWebSocketInstance();
		ws.disconnect();
		authStore.logout();
		goto('/login');
	}

	// Check if current page requires authentication
	let isLoginPage = $derived($page.url.pathname === '/login');
	let requiresAuth = $derived(!isLoginPage);
</script>

<svelte:head>
	<title>AXME Production System</title>
	<meta name="description" content="Industrial Production Monitoring and Control System" />
</svelte:head>

{#if requiresAuth && $authStore.isAuthenticated}
	<!-- Authenticated Layout with Navigation -->
	<div class="h-screen grid grid-rows-[auto_1fr]">
		<!-- Header -->
		<header class="bg-surface-100-900 border-b border-surface-300-700 px-6 py-4">
			<div class="flex items-center justify-between">
				<div class="flex items-center space-x-4">
					<h1 class="text-2xl font-bold text-primary-500">🏭 AXME Production</h1>
				</div>
				
				<div class="flex items-center space-x-4">
					<span class="text-sm text-surface-700-300">
						Welcome, {$authStore.user?.full_name || $authStore.user?.username}
					</span>
					<span class="badge preset-filled-surface text-xs">
						{$authStore.user?.role?.toUpperCase()}
					</span>
					<button 
						class="btn preset-tonal-error btn-sm"
						onclick={handleLogout}
					>
						Logout
					</button>
				</div>
			</div>
		</header>

		<!-- Main Content with Sidebar -->
		<div class="grid grid-cols-[auto_1fr] h-full">
			<!-- Sidebar Navigation -->
			<aside class="w-64 bg-surface-50-950 border-r border-surface-300-700">
				<nav class="p-4">
					<ul class="space-y-2">
						{#each navItems as item}
							{#if !item.requireRole || $authStore.user?.role === item.requireRole}
								<li>
									<a
										href={item.href}
										class="flex items-center space-x-3 px-4 py-2 rounded-lg text-surface-700-300 hover:bg-surface-200-800 hover:text-primary-500 transition-colors"
										class:bg-primary-500={$page.url.pathname === item.href}
										class:text-white={$page.url.pathname === item.href}
									>
										<span class="text-lg">{item.icon}</span>
										<span>{item.label}</span>
									</a>
								</li>
							{/if}
						{/each}
					</ul>
				</nav>
			</aside>

			<!-- Main Content Area -->
			<main class="overflow-auto">
				{@render children()}
			</main>
		</div>
	</div>
{:else if isLoginPage}
	<!-- Login Page Layout -->
	{@render children()}
{:else}
	<!-- Redirect to login if not authenticated -->
	<div class="h-screen flex items-center justify-center">
		<div class="text-center">
			<h1 class="text-2xl font-bold mb-4">Redirecting to login...</h1>
			<div class="loading-spinner"></div>
		</div>
	</div>
	<script>
		// Client-side redirect
		if (typeof window !== 'undefined') {
			window.location.href = '/login';
		}
	</script>
{/if}
