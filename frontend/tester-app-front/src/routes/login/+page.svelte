<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	
	// Lucide Icons
	import User from '@lucide/svelte/icons/user';
	import Lock from '@lucide/svelte/icons/lock';
	import Eye from '@lucide/svelte/icons/eye';
	import EyeOff from '@lucide/svelte/icons/eye-off';
	import Factory from '@lucide/svelte/icons/factory';
	import Shield from '@lucide/svelte/icons/shield';
	import Settings from '@lucide/svelte/icons/settings';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import LogIn from '@lucide/svelte/icons/log-in';
	import AlertCircle from '@lucide/svelte/icons/alert-circle';

	// Form state
	let username = '';
	let password = '';
	let selectedRole = 'operator';
	let showPassword = false;
	let isLoading = false;
	let errorMessage = '';
	let rememberMe = false;

	// Animation state
	let mounted = false;

	// Role options
	const roles = [
		{ value: 'operator', label: 'Operator', icon: User, description: 'Production line operation' },
		{ value: 'supervisor', label: 'Supervisor', icon: Shield, description: 'Team and quality oversight' },
		{ value: 'admin', label: 'Administrator', icon: Settings, description: 'System configuration' }
	];

	onMount(() => {
		mounted = true;
		// Check for saved credentials
		const savedUsername = localStorage.getItem('saved_username');
		const savedRole = localStorage.getItem('saved_role');
		if (savedUsername) {
			username = savedUsername;
			rememberMe = true;
		}
		if (savedRole) {
			selectedRole = savedRole;
		}
	});

	function togglePasswordVisibility() {
		showPassword = !showPassword;
	}

	async function handleLogin() {
		if (!username.trim() || !password.trim()) {
			errorMessage = 'Please enter both username and password';
			return;
		}

		isLoading = true;
		errorMessage = '';

		try {
			// Simulate API call
			await new Promise(resolve => setTimeout(resolve, 1500));
			
			// Save credentials if remember me is checked
			if (rememberMe) {
				localStorage.setItem('saved_username', username);
				localStorage.setItem('saved_role', selectedRole);
			} else {
				localStorage.removeItem('saved_username');
				localStorage.removeItem('saved_role');
			}

			// Store user session
			sessionStorage.setItem('user_role', selectedRole);
			sessionStorage.setItem('user_name', username);
			
			// Redirect to dashboard
			goto('/home');
		} catch (error) {
			errorMessage = 'Login failed. Please check your credentials.';
		} finally {
			isLoading = false;
		}
	}

	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			handleLogin();
		}
	}

	$: selectedRoleData = roles.find(role => role.value === selectedRole);
</script>

<svelte:head>
	<title>AXME Industrial - Login</title>
</svelte:head>

<main class="min-h-screen bg-gradient-to-br from-surface-50 to-surface-200 dark:from-surface-900 dark:to-surface-950 flex items-center justify-center p-4">
	<!-- Background Pattern -->
	<div class="absolute inset-0 opacity-5">
		<div class="absolute inset-0" style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.3) 1px, transparent 0); background-size: 20px 20px;"></div>
	</div>

	<!-- Login Container -->
	<div class="relative w-full max-w-md">
		<!-- Main Login Card -->
		<div class="card preset-filled-surface-100-900 p-8 shadow-2xl border border-surface-200-800 backdrop-blur-sm"
			 class:scale-95={!mounted}
			 class:opacity-0={!mounted}
			 style="transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);">
			
			<!-- Header -->
			<header class="text-center mb-8">
				<div class="flex justify-center mb-4">
					<div class="p-4 rounded-full bg-primary-500/10 border border-primary-500/20">
						<Factory size={48} class="text-primary-500" />
					</div>
				</div>
				<h1 class="h1 text-2xl font-bold mb-2">AXME Industrial</h1>
				<p class="text-surface-600-400 text-sm">Production Management System</p>
			</header>

			<!-- Error Message -->
			{#if errorMessage}
				<div class="alert preset-filled-error-500 mb-6 flex items-center gap-2 p-3 rounded-container text-sm"
					 style="animation: shake 0.5s ease-in-out;">
					<AlertCircle size={16} />
					<span>{errorMessage}</span>
				</div>
			{/if}

			<!-- Login Form -->
			<form on:submit|preventDefault={handleLogin} class="space-y-6">
				<!-- Role Selection -->
				<div class="space-y-2">
					<label class="label">
						<span class="label-text text-sm font-medium">Access Level</span>
					</label>
					<div class="relative">
						<select bind:value={selectedRole} 
								class="select w-full appearance-none pr-10 bg-surface-50-950 border-surface-300-700">
							{#each roles as role}
								<option value={role.value}>{role.label} - {role.description}</option>
							{/each}
						</select>
						<ChevronDown size={16} class="absolute right-3 top-1/2 transform -translate-y-1/2 text-surface-500 pointer-events-none" />
					</div>
				</div>

				<!-- Username Input -->
				<div class="space-y-2">
					<label class="label">
						<span class="label-text text-sm font-medium">Username</span>
					</label>
					<div class="input-group grid-cols-[auto_1fr]">
						<div class="ig-cell preset-tonal">
							<User size={16} />
						</div>
						<input bind:value={username}
							   type="text"
							   placeholder="Enter your username"
							   class="ig-input"
							   on:keypress={handleKeyPress}
							   disabled={isLoading}
							   autocomplete="username" />
					</div>
				</div>

				<!-- Password Input -->
				<div class="space-y-2">
					<label class="label">
						<span class="label-text text-sm font-medium">Password</span>
					</label>
					<div class="input-group grid-cols-[auto_1fr_auto]">
						<div class="ig-cell preset-tonal">
							<Lock size={16} />
						</div>
						<input bind:value={password}
							   type={showPassword ? 'text' : 'password'}
							   placeholder="Enter your password"
							   class="ig-input"
							   on:keypress={handleKeyPress}
							   disabled={isLoading}
							   autocomplete="current-password" />
						<button type="button"
								class="ig-btn preset-tonal hover:preset-filled"
								on:click={togglePasswordVisibility}
								disabled={isLoading}>
							{#if showPassword}
								<EyeOff size={16} />
							{:else}
								<Eye size={16} />
							{/if}
						</button>
					</div>
				</div>

				<!-- Remember Me -->
				<div class="flex items-center space-x-2">
					<input type="checkbox" 
						   class="checkbox" 
						   bind:checked={rememberMe}
						   disabled={isLoading}
						   id="remember" />
					<label for="remember" class="text-sm text-surface-700-300 cursor-pointer">
						Remember my credentials
					</label>
				</div>

				<!-- Login Button -->
				<button type="submit"
						class="btn preset-filled-primary-500 w-full flex items-center justify-center gap-2 py-3"
						disabled={isLoading || !username.trim() || !password.trim()}
						class:animate-pulse={isLoading}>
					{#if isLoading}
						<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
						<span>Authenticating...</span>
					{:else}
						<LogIn size={16} />
						<span>Sign In</span>
					{/if}
				</button>
			</form>

			<!-- Selected Role Display -->
			{#if selectedRoleData}
				<div class="mt-6 p-4 rounded-container bg-surface-50-950 border border-surface-200-800">
					<div class="flex items-center gap-3">
						<div class="p-2 rounded-full bg-primary-500/10">
							<svelte:component this={selectedRoleData.icon} size={16} class="text-primary-500" />
						</div>
						<div>
							<p class="font-medium text-sm">{selectedRoleData.label}</p>
							<p class="text-xs text-surface-600-400">{selectedRoleData.description}</p>
						</div>
					</div>
				</div>
			{/if}
		</div>

		<!-- Footer -->
		<footer class="text-center mt-6 text-xs text-surface-600-400">
			<p>© 2024 AXME Industrial Systems. All rights reserved.</p>
			<p class="mt-1">Version 2.1.3 | Build 20241201</p>
		</footer>
	</div>
</main>
