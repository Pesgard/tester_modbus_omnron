<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { adminApi } from '$lib/services/api';
	import type { User } from '$lib/stores/auth';

	let users: User[] = [];
	let isLoading = false;
	let error = '';
	let showCreateForm = false;

	// Form data for creating new user
	let newUser = {
		username: '',
		email: '',
		password: '',
		full_name: '',
		role: 'operator' as 'admin' | 'supervisor' | 'operator' | 'viewer'
	};

	// Form validation
	let formErrors: Record<string, string> = {};

	onMount(() => {
		// Check if user has admin role
		if ($authStore.user?.role !== 'admin') {
			error = 'Access denied. Admin privileges required.';
			return;
		}
		
		loadUsers();
	});

	async function loadUsers() {
		isLoading = true;
		error = '';

		try {
			users = await adminApi.getUsers();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load users';
		} finally {
			isLoading = false;
		}
	}

	function validateForm(): boolean {
		formErrors = {};

		if (!newUser.username.trim()) {
			formErrors.username = 'Username is required';
		}

		if (!newUser.email.trim()) {
			formErrors.email = 'Email is required';
		} else if (!/\S+@\S+\.\S+/.test(newUser.email)) {
			formErrors.email = 'Please enter a valid email address';
		}

		if (!newUser.password) {
			formErrors.password = 'Password is required';
		} else if (newUser.password.length < 6) {
			formErrors.password = 'Password must be at least 6 characters';
		}

		return Object.keys(formErrors).length === 0;
	}

	async function handleCreateUser() {
		if (!validateForm()) return;

		isLoading = true;
		error = '';

		try {
			const createdUser = await adminApi.createUser({
				username: newUser.username.trim(),
				email: newUser.email.trim(),
				password: newUser.password,
				full_name: newUser.full_name.trim() || undefined,
				role: newUser.role
			});

			users = [...users, createdUser];
			
			// Reset form
			newUser = {
				username: '',
				email: '',
				password: '',
				full_name: '',
				role: 'operator'
			};
			formErrors = {};
			showCreateForm = false;

		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to create user';
		} finally {
			isLoading = false;
		}
	}

	function cancelCreateUser() {
		showCreateForm = false;
		newUser = {
			username: '',
			email: '',
			password: '',
			full_name: '',
			role: 'operator'
		};
		formErrors = {};
	}

	function getRoleBadgeClass(role: string): string {
		switch (role) {
			case 'admin': return 'preset-filled-error';
			case 'supervisor': return 'preset-filled-warning';
			case 'operator': return 'preset-filled-primary';
			case 'viewer': return 'preset-filled-surface';
			default: return 'preset-filled-surface';
		}
	}

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleString();
	}
</script>

<svelte:head>
	<title>Admin Panel - AXME Production System</title>
</svelte:head>

<div class="p-6 space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold">Admin Panel</h1>
			<p class="text-surface-600-400">User management and system administration</p>
		</div>
		
		{#if $authStore.user?.role === 'admin'}
			<button 
				class="btn preset-filled-primary"
				on:click={() => showCreateForm = true}
				disabled={showCreateForm || isLoading}
			>
				➕ Create User
			</button>
		{/if}
	</div>

	<!-- Access Denied Message -->
	{#if $authStore.user?.role !== 'admin'}
		<div class="alert preset-filled-error">
			<div class="alert-message">
				<h3 class="h4">Access Denied</h3>
				<p>Admin privileges required to access this page.</p>
			</div>
		</div>
	{:else}
		<!-- Error Message -->
		{#if error}
			<div class="alert preset-filled-error">
				<div class="alert-message">
					<h3 class="h4">Error</h3>
					<p>{error}</p>
				</div>
			</div>
		{/if}

		<!-- Create User Form -->
		{#if showCreateForm}
			<div class="card preset-outlined p-6">
				<h2 class="text-xl font-bold mb-4">Create New User</h2>
				
				<form on:submit|preventDefault={handleCreateUser} class="space-y-4">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<!-- Username -->
						<div class="space-y-2">
							<label for="username" class="label">Username *</label>
							<input
								id="username"
								type="text"
								class="input"
								class:input-error={formErrors.username}
								placeholder="Enter username"
								bind:value={newUser.username}
								disabled={isLoading}
								required
							/>
							{#if formErrors.username}
								<p class="text-error-500 text-sm">{formErrors.username}</p>
							{/if}
						</div>

						<!-- Email -->
						<div class="space-y-2">
							<label for="email" class="label">Email *</label>
							<input
								id="email"
								type="email"
								class="input"
								class:input-error={formErrors.email}
								placeholder="Enter email address"
								bind:value={newUser.email}
								disabled={isLoading}
								required
							/>
							{#if formErrors.email}
								<p class="text-error-500 text-sm">{formErrors.email}</p>
							{/if}
						</div>

						<!-- Full Name -->
						<div class="space-y-2">
							<label for="fullName" class="label">Full Name</label>
							<input
								id="fullName"
								type="text"
								class="input"
								placeholder="Enter full name (optional)"
								bind:value={newUser.full_name}
								disabled={isLoading}
							/>
						</div>

						<!-- Role -->
						<div class="space-y-2">
							<label for="role" class="label">Role *</label>
							<select
								id="role"
								class="select"
								bind:value={newUser.role}
								disabled={isLoading}
								required
							>
								<option value="viewer">Viewer</option>
								<option value="operator">Operator</option>
								<option value="supervisor">Supervisor</option>
								<option value="admin">Admin</option>
							</select>
						</div>
					</div>

					<!-- Password -->
					<div class="space-y-2">
						<label for="password" class="label">Password *</label>
						<input
							id="password"
							type="password"
							class="input"
							class:input-error={formErrors.password}
							placeholder="Enter password (min 6 characters)"
							bind:value={newUser.password}
							disabled={isLoading}
							required
						/>
						{#if formErrors.password}
							<p class="text-error-500 text-sm">{formErrors.password}</p>
						{/if}
					</div>

					<!-- Form Actions -->
					<div class="flex justify-end space-x-2">
						<button
							type="button"
							class="btn preset-tonal-surface"
							on:click={cancelCreateUser}
							disabled={isLoading}
						>
							Cancel
						</button>
						<button
							type="submit"
							class="btn preset-filled-primary"
							disabled={isLoading}
						>
							{#if isLoading}
								Creating...
							{:else}
								Create User
							{/if}
						</button>
					</div>
				</form>
			</div>
		{/if}

		<!-- Users List -->
		{#if isLoading && users.length === 0}
			<div class="flex items-center justify-center h-64">
				<div class="text-center">
					<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
					<p class="text-surface-600-400">Loading users...</p>
				</div>
			</div>
		{:else if users.length === 0}
			<div class="card preset-outlined p-12 text-center">
				<div class="text-6xl mb-4">👥</div>
				<h3 class="text-xl font-bold mb-2">No Users Found</h3>
				<p class="text-surface-600-400">
					No users found in the system.
				</p>
			</div>
		{:else}
			<div class="card preset-outlined overflow-hidden">
				<div class="overflow-x-auto">
					<table class="table table-hover">
						<thead>
							<tr>
								<th>User</th>
								<th>Email</th>
								<th>Role</th>
								<th>Status</th>
								<th>Last Login</th>
								<th>Created</th>
							</tr>
						</thead>
						<tbody>
							{#each users as user}
								<tr>
									<td>
										<div class="flex flex-col">
											<span class="font-semibold">{user.full_name || user.username}</span>
											{#if user.full_name}
												<span class="text-sm text-surface-600-400 font-mono">@{user.username}</span>
											{/if}
										</div>
									</td>
									<td class="font-mono text-sm">
										{user.email}
									</td>
									<td>
										<span class="badge {getRoleBadgeClass(user.role)} text-xs">
											{user.role.toUpperCase()}
										</span>
									</td>
									<td>
										<span class="badge {user.is_active ? 'preset-filled-success' : 'preset-filled-error'} text-xs">
											{user.is_active ? 'ACTIVE' : 'INACTIVE'}
										</span>
									</td>
									<td class="font-mono text-sm">
										{user.last_login ? formatDate(user.last_login) : 'Never'}
									</td>
									<td class="font-mono text-sm">
										{formatDate(user.created_at)}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>

			<!-- Summary -->
			<div class="text-center text-sm text-surface-600-400">
				Total users: {users.length}
			</div>
		{/if}
	{/if}
</div>