<script lang="ts">
	import type { PageData, ActionData } from './$types';
	import { enhance } from '$app/forms';
	import IconPlus from '@lucide/svelte/icons/plus';
	import IconEdit from '@lucide/svelte/icons/edit';
	import IconTrash from '@lucide/svelte/icons/trash';
	import IconPower from '@lucide/svelte/icons/power';
	import IconKey from '@lucide/svelte/icons/key';
	import IconShield from '@lucide/svelte/icons/shield';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	let showModal = $state(false);
	let showPasswordModal = $state(false);
	let showRolesModal = $state(false);
	let editingUser = $state<any>(null);
	let searchQuery = $state('');
	let activeFilter = $state<'all' | 'active' | 'inactive'>('all');

	const filteredUsers = $derived(
		data.users.filter((user) => {
			const matchesSearch = user.username.toLowerCase().includes(searchQuery.toLowerCase());
			const matchesStatus =
				activeFilter === 'all' ||
				(activeFilter === 'active' && user.active) ||
				(activeFilter === 'inactive' && !user.active);
			return matchesSearch && matchesStatus;
		})
	);

	function hasPermission(permission: string): boolean {
		if (!data.user?.permisos) return false;
		if (data.user.permisos.includes('*')) return true;
		if (data.user.permisos.includes(permission)) return true;
		const [namespace] = permission.split('.');
		return data.user.permisos.includes(`${namespace}.*`);
	}

	const canCreate = $derived(hasPermission('management.usuarios.crear'));
	const canEdit = $derived(hasPermission('management.usuarios.editar'));
	const canDelete = $derived(hasPermission('management.usuarios.eliminar'));
	const canToggle = $derived(hasPermission('management.usuarios.activar'));
	const canPassword = $derived(hasPermission('management.usuarios.password'));
	const canRoles = $derived(hasPermission('management.usuarios.roles'));

	function openCreateModal() {
		editingUser = null;
		showModal = true;
	}

	function openEditModal(user: any) {
		editingUser = user;
		showModal = true;
	}

	function openPasswordModal(user: any) {
		editingUser = user;
		showPasswordModal = true;
	}

	function openRolesModal(user: any) {
		editingUser = user;
		showRolesModal = true;
	}

	function closeModal() {
		showModal = false;
		showPasswordModal = false;
		showRolesModal = false;
		editingUser = null;
	}
</script>

<div class="usuarios-page p-6 h-full overflow-auto">
	<div class="flex items-center justify-between mb-6">
		<div>
			<h1 class="text-3xl font-bold">Users Management</h1>
			<p class="text-surface-600-400 mt-1">Manage user accounts and access</p>
		</div>
		{#if canCreate}
			<button class="btn variant-filled-primary" onclick={openCreateModal}>
				<IconPlus size={20} />
				<span>New User</span>
			</button>
		{/if}
	</div>

	<!-- Notifications -->
	{#if form?.success}
		<aside class="alert variant-filled-success">
			<div class="alert-message">
				<p>{form.message}</p>
			</div>
		</aside>
	{:else if form?.error}
		<aside class="alert variant-filled-error">
			<div class="alert-message">
				<p>{form.error}</p>
			</div>
		</aside>
	{/if}

	<!-- Filters -->
	<div class="card variant-glass-surface p-4 mb-6">
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<input
				type="search"
				class="input"
				placeholder="Search by username..."
				bind:value={searchQuery}
			/>
			<select class="select" bind:value={activeFilter}>
				<option value="all">All Users</option>
				<option value="active">Active Only</option>
				<option value="inactive">Inactive Only</option>
			</select>
		</div>
	</div>

	<!-- Users Table -->
	<div class="card variant-glass-surface p-6">
		<div class="table-container">
			<table class="table table-hover">
				<thead>
					<tr>
						<th>Status</th>
						<th>Username</th>
						<th>Roles</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each filteredUsers as user}
						<tr class:opacity-50={!user.active}>
							<td>
								<span class="badge" class:variant-filled-success={user.active} class:variant-filled-error={!user.active}>
									{user.active ? 'Active' : 'Inactive'}
								</span>
							</td>
							<td class="font-semibold">{user.username}</td>
							<td>
								<div class="flex flex-wrap gap-1">
									{#each user.roles as userRole}
										<span class="badge variant-soft-primary">{userRole.role.name}</span>
									{/each}
									{#if user.roles.length === 0}
										<span class="text-sm text-surface-600-400">No roles assigned</span>
									{/if}
								</div>
							</td>
							<td>
								<div class="flex gap-2">
									{#if canToggle && user.id !== data.user?.id}
										<form method="POST" action="?/toggle" use:enhance>
											<input type="hidden" name="id" value={user.id} />
											<input type="hidden" name="active" value={user.active} />
											<button type="submit" class="btn btn-sm variant-ghost" title="Toggle Status">
												<IconPower
													size={16}
													class={user.active ? 'text-success-500' : 'text-surface-500'}
												/>
											</button>
										</form>
									{/if}

									{#if canPassword}
										<button
											class="btn btn-sm variant-ghost"
											onclick={() => openPasswordModal(user)}
											title="Change Password"
										>
											<IconKey size={16} />
										</button>
									{/if}

									{#if canRoles}
										<button
											class="btn btn-sm variant-ghost"
											onclick={() => openRolesModal(user)}
											title="Manage Roles"
										>
											<IconShield size={16} />
										</button>
									{/if}

									{#if canEdit}
										<button
											class="btn btn-sm variant-ghost"
											onclick={() => openEditModal(user)}
											title="Edit"
										>
											<IconEdit size={16} />
										</button>
									{/if}

									{#if canDelete && user.id !== data.user?.id}
										<form method="POST" action="?/delete" use:enhance>
											<input type="hidden" name="id" value={user.id} />
											<button
												type="submit"
												class="btn btn-sm variant-ghost-error"
												title="Delete"
												onclick={(e) => {
													if (!confirm('Are you sure you want to delete this user?')) {
														e.preventDefault();
													}
												}}
											>
												<IconTrash size={16} />
											</button>
										</form>
									{/if}
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>

			{#if filteredUsers.length === 0}
				<div class="text-center py-12 text-surface-600-400">No users found</div>
			{/if}
		</div>
	</div>
</div>

<!-- Create/Edit User Modal -->
{#if showModal}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="modal-backdrop" onclick={closeModal}>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="modal variant-filled-surface p-8 w-modal space-y-4" onclick={(e) => e.stopPropagation()}>
			<header class="modal-header">
				<h2 class="h2">{editingUser ? 'Edit User' : 'Create New User'}</h2>
			</header>

			<form
				method="POST"
				action={editingUser ? '?/update' : '?/create'}
				use:enhance={() => {
					return async ({ result }) => {
						if (result.type === 'success') {
							closeModal();
						}
					};
				}}
			>
				{#if editingUser}
					<input type="hidden" name="id" value={editingUser.id} />
				{/if}

				<div class="space-y-4">
					<label class="label">
						<span>Username *</span>
						<input
							name="username"
							type="text"
							class="input"
							value={editingUser?.username || ''}
							required
						/>
					</label>

					{#if !editingUser}
						<label class="label">
							<span>Password *</span>
							<input
								name="password"
								type="password"
								class="input"
								minlength="6"
								required
							/>
						</label>

						<div>
							<span class="label-text mb-3">Assign Roles</span>
							<div class="space-y-2">
								{#each data.roles as role}
									<label class="flex items-center space-x-2">
										<input type="checkbox" name="roles" value={role.id} class="checkbox" />
										<span>{role.name}</span>
										<span class="text-xs text-surface-600-400">- {role.description}</span>
									</label>
								{/each}
							</div>
						</div>
					{/if}

					<label class="flex items-center space-x-2">
						<input type="checkbox" name="active" class="checkbox" checked={editingUser?.active ?? true} />
						<span>Active User</span>
					</label>
				</div>

				<footer class="modal-footer flex justify-end gap-4">
					<button type="button" class="btn variant-ghost" onclick={closeModal}> Cancel </button>
					<button type="submit" class="btn variant-filled-primary">
						{editingUser ? 'Update' : 'Create'}
					</button>
				</footer>
			</form>
		</div>
	</div>
{/if}

<!-- Change Password Modal -->
{#if showPasswordModal}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="modal-backdrop" onclick={closeModal}>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="modal variant-filled-surface p-8 w-modal space-y-4" onclick={(e) => e.stopPropagation()}>
			<header class="modal-header">
				<h2 class="h2">Change Password</h2>
			</header>

			<form
				method="POST"
				action="?/changePassword"
				use:enhance={() => {
					return async ({ result }) => {
						if (result.type === 'success') {
							closeModal();
						}
					};
				}}
			>
				<input type="hidden" name="id" value={editingUser?.id} />

				<div class="space-y-4">
					<p class="text-sm text-surface-600-400">
						Changing password for: <strong>{editingUser?.username}</strong>
					</p>

					<label class="label">
						<span>New Password *</span>
						<input
							name="new_password"
							type="password"
							class="input"
							minlength="6"
							required
						/>
					</label>
				</div>

				<footer class="modal-footer flex justify-end gap-4">
					<button type="button" class="btn variant-ghost" onclick={closeModal}> Cancel </button>
					<button type="submit" class="btn variant-filled-primary"> Update Password </button>
				</footer>
			</form>
		</div>
	</div>
{/if}

<!-- Manage Roles Modal -->
{#if showRolesModal}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="modal-backdrop" onclick={closeModal}>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="modal variant-filled-surface p-8 w-modal space-y-4" onclick={(e) => e.stopPropagation()}>
			<header class="modal-header">
				<h2 class="h2">Manage User Roles</h2>
			</header>

			<form
				method="POST"
				action="?/updateRoles"
				use:enhance={() => {
					return async ({ result }) => {
						if (result.type === 'success') {
							closeModal();
						}
					};
				}}
			>
				<input type="hidden" name="user_id" value={editingUser?.id} />

				<div class="space-y-4">
					<p class="text-sm text-surface-600-400">
						Managing roles for: <strong>{editingUser?.username}</strong>
					</p>

					<div>
						<span class="label-text mb-3">Select Roles</span>
						<div class="space-y-3">
							{#each data.roles as role}
								{@const isAssigned = editingUser?.roles.some(
									(ur: any) => ur.role.id === role.id
								)}
								<label class="flex items-start space-x-2">
									<input
										type="checkbox"
										name="roles"
										value={role.id}
										class="checkbox mt-1"
										checked={isAssigned}
									/>
									<div>
										<div class="font-semibold">{role.name}</div>
										<div class="text-xs text-surface-600-400">{role.description}</div>
									</div>
								</label>
							{/each}
						</div>
					</div>
				</div>

				<footer class="modal-footer flex justify-end gap-4">
					<button type="button" class="btn variant-ghost" onclick={closeModal}> Cancel </button>
					<button type="submit" class="btn variant-filled-primary"> Update Roles </button>
				</footer>
			</form>
		</div>
	</div>
{/if}

<style>
	.modal-backdrop {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.8);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		backdrop-filter: blur(4px);
	}
</style>
