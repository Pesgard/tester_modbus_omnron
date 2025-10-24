<script lang="ts">
	import type { PageData, ActionData } from './$types';
	import { enhance } from '$app/forms';
	import IconPlus from '@lucide/svelte/icons/plus';
	import IconEdit from '@lucide/svelte/icons/edit';
	import IconTrash from '@lucide/svelte/icons/trash';
	import IconShield from '@lucide/svelte/icons/shield';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	let showModal = $state(false);
	let showPermissionsModal = $state(false);
	let editingRole = $state<any>(null);
	let searchQuery = $state('');
	let selectedCategory = $state('all');

	const filteredRoles = $derived(
		data.roles.filter((role) =>
			role.name.toLowerCase().includes(searchQuery.toLowerCase())
		)
	);

	// Group permissions by category
	const permissionsByCategory = $derived.by(() => {
		const categories = new Map<string, any[]>();
		for (const permiso of data.allPermisos) {
			const category = permiso.key.split('.')[0];
			if (!categories.has(category)) {
				categories.set(category, []);
			}
			categories.get(category)!.push(permiso);
		}
		return categories;
	});

	function hasPermission(permission: string): boolean {
		if (!data.user?.permisos) return false;
		if (data.user.permisos.includes('*')) return true;
		if (data.user.permisos.includes(permission)) return true;
		const [namespace] = permission.split('.');
		return data.user.permisos.includes(`${namespace}.*`);
	}

	const canCreate = $derived(hasPermission('management.roles.crear'));
	const canEdit = $derived(hasPermission('management.roles.editar'));
	const canDelete = $derived(hasPermission('management.roles.eliminar'));
	const canPermissions = $derived(hasPermission('management.roles.permisos'));

	function openCreateModal() {
		editingRole = null;
		showModal = true;
	}

	function openEditModal(role: any) {
		editingRole = role;
		showModal = true;
	}

	function openPermissionsModal(role: any) {
		editingRole = role;
		showPermissionsModal = true;
	}

	function closeModal() {
		showModal = false;
		showPermissionsModal = false;
		editingRole = null;
	}
</script>

<div class="roles-page p-6 h-full overflow-auto">
	<div class="flex items-center justify-between mb-6">
		<div>
			<h1 class="text-3xl font-bold">Roles & Permissions</h1>
			<p class="text-surface-600-400 mt-1">Manage user roles and their permissions</p>
		</div>
		{#if canCreate}
			<button class="btn variant-filled-primary" onclick={openCreateModal}>
				<IconPlus size={20} />
				<span>New Role</span>
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

	<!-- Search -->
	<div class="card variant-glass-surface p-4 mb-6">
		<input
			type="search"
			class="input"
			placeholder="Search by role name..."
			bind:value={searchQuery}
		/>
	</div>

	<!-- Roles Table -->
	<div class="card variant-glass-surface p-6">
		<div class="table-container">
			<table class="table table-hover">
				<thead>
					<tr>
						<th>Role Name</th>
						<th>Description</th>
						<th>Permissions</th>
						<th>Users</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each filteredRoles as role}
						<tr>
							<td class="font-semibold">{role.name}</td>
							<td class="max-w-xs">
								<div class="truncate" title={role.description}>
									{role.description}
								</div>
							</td>
							<td>
								<span class="badge variant-soft">{(role as any).permisosRol?.length || 0}</span>
							</td>
							<td>
								<div class="flex flex-wrap gap-1">
									{#each ((role as any).userRoles || []).slice(0, 3) as userRole}
										<span class="badge variant-soft-primary text-xs">{userRole.user.username}</span>
									{/each}
									{#if ((role as any).userRoles?.length || 0) > 3}
										<span class="text-xs text-surface-600-400"
											>+{((role as any).userRoles.length || 0) - 3} more</span
										>
									{/if}
								</div>
							</td>
							<td>
								<div class="flex gap-2">
									{#if canPermissions}
										<button
											class="btn btn-sm variant-ghost"
											onclick={() => openPermissionsModal(role)}
											title="Manage Permissions"
										>
											<IconShield size={16} />
										</button>
									{/if}

									{#if canEdit}
										<button
											class="btn btn-sm variant-ghost"
											onclick={() => openEditModal(role)}
											title="Edit"
										>
											<IconEdit size={16} />
										</button>
									{/if}

									{#if canDelete && ((role as any).userRoles?.length || 0) === 0}
										<form method="POST" action="?/deleteRole" use:enhance>
											<input type="hidden" name="id" value={role.id} />
											<button
												type="submit"
												class="btn btn-sm variant-ghost-error"
												title="Delete"
												onclick={(e) => {
													if (!confirm('Are you sure you want to delete this role?')) {
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

			{#if filteredRoles.length === 0}
				<div class="text-center py-12 text-surface-600-400">No roles found</div>
			{/if}
		</div>
	</div>
</div>

<!-- Create/Edit Role Modal -->
{#if showModal}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="modal-backdrop" onclick={closeModal}>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="modal variant-filled-surface p-8 w-modal space-y-4" onclick={(e) => e.stopPropagation()}>
			<header class="modal-header">
				<h2 class="h2">{editingRole ? 'Edit Role' : 'Create New Role'}</h2>
			</header>

			<form
				method="POST"
				action={editingRole ? '?/updateRole' : '?/createRole'}
				use:enhance={() => {
					return async ({ result }) => {
						if (result.type === 'success') {
							closeModal();
						}
					};
				}}
			>
				{#if editingRole}
					<input type="hidden" name="id" value={editingRole.id} />
				{/if}

				<div class="space-y-4">
					<label class="label">
						<span>Role Name *</span>
						<input
							name="name"
							type="text"
							class="input"
							value={editingRole?.name || ''}
							required
						/>
					</label>

					<label class="label">
						<span>Description *</span>
						<textarea
							name="description"
							class="textarea"
							rows="3"
							value={editingRole?.description || ''}
							required
						></textarea>
					</label>

					{#if !editingRole}
						<div>
							<span class="label-text mb-3">Select Permissions</span>
							<div class="max-h-64 overflow-y-auto space-y-4 card variant-glass p-4">
								{#each Array.from(permissionsByCategory.entries()) as [category, permisos]}
									<div>
										<div class="font-semibold mb-2 text-primary-500 capitalize">
											{category}
										</div>
										<div class="space-y-2 pl-4">
											{#each permisos as permiso}
												<label class="flex items-start space-x-2">
													<input
														type="checkbox"
														name="permisos"
														value={permiso.id}
														class="checkbox mt-1"
													/>
													<div>
														<div class="text-sm font-mono">{permiso.key}</div>
														<div class="text-xs text-surface-600-400">{permiso.description}</div>
													</div>
												</label>
											{/each}
										</div>
									</div>
								{/each}
							</div>
						</div>
					{/if}
				</div>

				<footer class="modal-footer flex justify-end gap-4">
					<button type="button" class="btn variant-ghost" onclick={closeModal}> Cancel </button>
					<button type="submit" class="btn variant-filled-primary">
						{editingRole ? 'Update' : 'Create'}
					</button>
				</footer>
			</form>
		</div>
	</div>
{/if}

<!-- Manage Permissions Modal -->
{#if showPermissionsModal}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="modal-backdrop" onclick={closeModal}>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="modal variant-filled-surface p-8 w-modal-wide max-h-[90vh] overflow-y-auto space-y-4" onclick={(e) => e.stopPropagation()}>
			<header class="modal-header">
				<h2 class="h2">Manage Permissions</h2>
			</header>

			<form
				method="POST"
				action="?/updatePermissions"
				use:enhance={() => {
					return async ({ result }) => {
						if (result.type === 'success') {
							closeModal();
						}
					};
				}}
			>
				<input type="hidden" name="role_id" value={editingRole?.id} />

				<div class="space-y-4">
					<p class="text-sm text-surface-600-400">
						Managing permissions for: <strong>{editingRole?.name}</strong>
					</p>

					<!-- Category Filter -->
					<label class="label">
						<span>Filter by category</span>
						<select class="select" bind:value={selectedCategory}>
							<option value="all">All Categories</option>
							{#each Array.from(permissionsByCategory.keys()) as category}
								<option value={category} class="capitalize">{category}</option>
							{/each}
						</select>
					</label>

					<!-- Permissions List -->
					<div class="max-h-96 overflow-y-auto space-y-4 card variant-glass p-4">
						{#each Array.from(permissionsByCategory.entries()) as [category, permisos]}
							{#if selectedCategory === 'all' || selectedCategory === category}
								<div>
									<div class="font-semibold mb-2 text-primary-500 capitalize">
										{category}
									</div>
									<div class="space-y-2 pl-4">
										{#each permisos as permiso}
											{@const isAssigned = editingRole?.permisosRol.some(
												(pr: any) => pr.permiso.id === permiso.id
											)}
											<label class="flex items-start space-x-2">
												<input
													type="checkbox"
													name="permisos"
													value={permiso.id}
													class="checkbox mt-1"
													checked={isAssigned}
												/>
												<div>
													<div class="text-sm font-mono">{permiso.key}</div>
													<div class="text-xs text-surface-600-400">{permiso.description}</div>
												</div>
											</label>
										{/each}
									</div>
								</div>
							{/if}
						{/each}
					</div>
				</div>

				<footer class="modal-footer flex justify-end gap-4">
					<button type="button" class="btn variant-ghost" onclick={closeModal}> Cancel </button>
					<button type="submit" class="btn variant-filled-primary"> Update Permissions </button>
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
