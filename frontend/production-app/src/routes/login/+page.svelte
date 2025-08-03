<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { authApi } from '$lib/services/api';
	import { onMount } from 'svelte';

	let username = $state('');
	let password = $state('');
	let isLoading = $state(false);
	let error = $state('');

	// Redirect if already authenticated
	onMount(() => {
		if ($authStore.isAuthenticated) {
			goto('/');
		}
	});

	async function handleLogin() {
		if (!username || !password) {
			error = 'Please enter both username and password';
			return;
		}

		isLoading = true;
		error = '';
		authStore.setLoading(true);

		try {
			const response = await authApi.login({ username, password });
			authStore.login(response.access_token, response.user);
			goto('/');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Login failed';
		} finally {
			isLoading = false;
			authStore.setLoading(false);
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			handleLogin();
		}
	}
</script>

<svelte:head>
	<title>Login - AXME Production System</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 via-secondary-500 to-tertiary-500">
	<div class="w-full max-w-md">
		<!-- Login Card -->
		<div class="card preset-outlined bg-surface-50-950 p-8 space-y-6">
			<!-- Header -->
			<div class="text-center space-y-2">
				<div class="text-6xl">🏭</div>
				<h1 class="text-3xl font-bold text-surface-900-50">AXME Production</h1>
				<p class="text-surface-600-400">Industrial Monitoring System</p>
			</div>

			<!-- Login Form -->
			<form onsubmit={handleLogin} class="space-y-4">
				<!-- Username Field -->
				<div class="space-y-2">
					<label for="username" class="label">Username</label>
					<input
						id="username"
						type="text"
						class="input"
						placeholder="Enter your username"
						bind:value={username}
						disabled={isLoading}
						onkeydown={handleKeydown}
						required
					/>
				</div>

				<!-- Password Field -->
				<div class="space-y-2">
					<label for="password" class="label">Password</label>
					<input
						id="password"
						type="password"
						class="input"
						placeholder="Enter your password"
						bind:value={password}
						disabled={isLoading}
						onkeydown={handleKeydown}
						required
					/>
				</div>

				<!-- Error Message -->
				{#if error}
					<div class="alert preset-filled-error">
						<div class="alert-message">
							<p>{error}</p>
						</div>
					</div>
				{/if}

				<!-- Login Button -->
				<button
					type="submit"
					class="btn preset-filled-primary w-full"
					disabled={isLoading || !username || !password}
				>
					{#if isLoading}
						<span class="flex items-center justify-center">
							<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
							Signing in...
						</span>
					{:else}
						Sign In
					{/if}
				</button>
			</form>

			<!-- Demo Credentials -->
			<div class="border-t border-surface-300-700 pt-4">
				<p class="text-sm text-surface-600-400 text-center mb-3">Demo Credentials:</p>
				<div class="grid grid-cols-2 gap-2 text-xs">
					<div class="card preset-tonal-surface p-2">
						<strong>Admin:</strong><br>
						admin / admin123
					</div>
					<div class="card preset-tonal-surface p-2">
						<strong>Operator:</strong><br>
						operator / op123
					</div>
				</div>
			</div>
		</div>

		<!-- Footer -->
		<div class="text-center text-white/70 mt-6 text-sm">
			© 2024 AXME Production System. All rights reserved.
		</div>
	</div>
</div>