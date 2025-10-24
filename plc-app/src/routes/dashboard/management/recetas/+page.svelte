<script lang="ts">
	import type { PageData, ActionData } from './$types';
	import { enhance } from '$app/forms';
	import IconPlus from '@lucide/svelte/icons/plus';
	import IconEdit from '@lucide/svelte/icons/edit';
	import IconTrash from '@lucide/svelte/icons/trash';
	import IconPower from '@lucide/svelte/icons/power';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	let showModal = $state(false);
	let editingReceta = $state<any>(null);
	let searchQuery = $state('');

	const filteredRecetas = $derived(
		data.recetas.filter(
			(receta) =>
				receta.ppn.toLowerCase().includes(searchQuery.toLowerCase()) ||
				receta.item_description.toLowerCase().includes(searchQuery.toLowerCase()) ||
				receta.cable_np.toLowerCase().includes(searchQuery.toLowerCase())
		)
	);

	function hasPermission(permission: string): boolean {
		if (!data.user?.permisos) return false;
		if (data.user.permisos.includes('*')) return true;
		if (data.user.permisos.includes(permission)) return true;
		const [namespace] = permission.split('.');
		return data.user.permisos.includes(`${namespace}.*`);
	}

	const canCreate = $derived(hasPermission('management.recetas.crear'));
	const canEdit = $derived(hasPermission('management.recetas.editar'));
	const canDelete = $derived(hasPermission('management.recetas.eliminar'));
	const canToggle = $derived(hasPermission('management.recetas.activar'));

	function openCreateModal() {
		editingReceta = null;
		showModal = true;
	}

	function openEditModal(receta: any) {
		editingReceta = receta;
		showModal = true;
	}

	function closeModal() {
		showModal = false;
		editingReceta = null;
	}
</script>

<div class="recetas-page p-6 h-full overflow-auto">
	<div class="flex items-center justify-between mb-6">
		<div>
			<h1 class="text-3xl font-bold">Recipes Management</h1>
			<p class="text-surface-600-400 mt-1">Manage cable recipes and specifications</p>
		</div>
		{#if canCreate}
			<button class="btn variant-filled-primary" onclick={openCreateModal}>
				<IconPlus size={20} />
				<span>New Recipe</span>
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
			placeholder="Search by PPN, description, or cable NP..."
			bind:value={searchQuery}
		/>
	</div>

	<!-- Recipes Table -->
	<div class="card variant-glass-surface p-6">
		<div class="table-container">
			<table class="table table-hover">
				<thead>
					<tr>
						<th>Status</th>
						<th>PPN</th>
						<th>Cable NP</th>
						<th>Description</th>
						<th>Quantity</th>
						<th>Conductors</th>
						<th>Terminals</th>
						<th>Lots</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each filteredRecetas as receta}
						<tr class:opacity-50={!receta.activa}>
							<td>
								<span class="badge" class:variant-filled-success={receta.activa} class:variant-filled-error={!receta.activa}>
									{receta.activa ? 'Active' : 'Inactive'}
								</span>
							</td>
							<td class="font-semibold font-mono">{receta.ppn}</td>
							<td class="font-mono text-sm">{receta.cable_np}</td>
							<td class="max-w-xs">
								<div class="truncate" title={receta.item_description}>
									{receta.item_description}
								</div>
							</td>
							<td>
								{receta.quantity} {receta.u_of_m}
							</td>
							<td class="text-center">{receta.cantidad_conductores}</td>
							<td class="text-sm">
								{#if receta.l1_terminal}L1: {receta.l1_terminal}<br />{/if}
								{#if receta.l2_terminal}L2: {receta.l2_terminal}{/if}
							</td>
							<td class="text-center">
								<span class="badge">{receta._count.lotes}</span>
							</td>
							<td>
								<div class="flex gap-2">
									{#if canToggle}
										<form method="POST" action="?/toggle" use:enhance>
											<input type="hidden" name="id" value={receta.id} />
											<input type="hidden" name="activa" value={receta.activa} />
											<button
												type="submit"
												class="btn btn-sm variant-ghost"
												title={receta.activa ? 'Deactivate' : 'Activate'}
											>
												<IconPower
													size={16}
													class={receta.activa ? 'text-success-500' : 'text-surface-500'}
												/>
											</button>
										</form>
									{/if}
									{#if canEdit}
										<button
											class="btn btn-sm variant-ghost"
											onclick={() => openEditModal(receta)}
											title="Edit"
										>
											<IconEdit size={16} />
										</button>
									{/if}
									{#if canDelete}
										<form method="POST" action="?/delete" use:enhance>
											<input type="hidden" name="id" value={receta.id} />
											<button
												type="submit"
												class="btn btn-sm variant-ghost-error"
												title="Delete"
												onclick={(e) => {
													if (!confirm('Are you sure you want to delete this recipe?')) {
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

			{#if filteredRecetas.length === 0}
				<div class="text-center py-12 text-surface-600-400">
					{#if searchQuery}
						No recipes found matching "{searchQuery}"
					{:else}
						No recipes yet. Create your first recipe!
					{/if}
				</div>
			{/if}
		</div>
	</div>
</div>

<!-- Modal -->
{#if showModal}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="modal-backdrop" onclick={closeModal}>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="modal variant-filled-surface p-8 w-modal space-y-4" onclick={(e) => e.stopPropagation()}>
			<header class="modal-header">
				<h2 class="h2">{editingReceta ? 'Edit Recipe' : 'Create New Recipe'}</h2>
			</header>

			<form
				method="POST"
				action={editingReceta ? '?/update' : '?/create'}
				use:enhance={() => {
					return async ({ result }) => {
						if (result.type === 'success') {
							closeModal();
						}
					};
				}}
			>
				{#if editingReceta}
					<input type="hidden" name="id" value={editingReceta.id} />
				{/if}

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label for="ppn" class="block text-sm font-medium mb-2">PPN *</label>
						<input
							id="ppn"
							name="ppn"
							type="text"
							class="input w-full"
							value={editingReceta?.ppn || ''}
							required
						/>
					</div>

					<div>
						<label for="cable_np" class="block text-sm font-medium mb-2">Cable NP *</label>
						<input
							id="cable_np"
							name="cable_np"
							type="text"
							class="input w-full"
							value={editingReceta?.cable_np || ''}
							required
						/>
					</div>

					<div>
						<label for="quantity" class="block text-sm font-medium mb-2">Quantity *</label>
						<input
							id="quantity"
							name="quantity"
							type="number"
							step="0.001"
							class="input w-full"
							value={editingReceta?.quantity || ''}
							required
						/>
					</div>

					<div>
						<label for="u_of_m" class="block text-sm font-medium mb-2">Unit *</label>
						<select
							id="u_of_m"
							name="u_of_m"
							class="select w-full"
							value={editingReceta?.u_of_m || 'FT'}
							required
						>
							<option value="FT">FT (Feet)</option>
							<option value="M">M (Meters)</option>
							<option value="IN">IN (Inches)</option>
						</select>
					</div>

					<div class="col-span-2">
						<label for="item_description" class="block text-sm font-medium mb-2"
							>Description *</label
						>
						<textarea
							id="item_description"
							name="item_description"
							class="input w-full"
							rows="2"
							value={editingReceta?.item_description || ''}
							required
						></textarea>
					</div>

					<div>
						<label for="cantidad_conductores" class="block text-sm font-medium mb-2"
							>Conductors *</label
						>
						<input
							id="cantidad_conductores"
							name="cantidad_conductores"
							type="number"
							min="1"
							max="5"
							class="input w-full"
							value={editingReceta?.cantidad_conductores || 4}
							required
						/>
					</div>

					<div>
						<label for="activa" class="flex items-center gap-2">
							<input
								id="activa"
								name="activa"
								type="checkbox"
								checked={editingReceta?.activa ?? true}
							/>
							<span>Active</span>
						</label>
					</div>

					<div>
						<label for="l1_terminal" class="block text-sm font-medium mb-2">L1 Terminal</label>
						<input
							id="l1_terminal"
							name="l1_terminal"
							type="text"
							class="input w-full"
							value={editingReceta?.l1_terminal || ''}
						/>
					</div>

					<div>
						<label for="l2_terminal" class="block text-sm font-medium mb-2">L2 Terminal</label>
						<input
							id="l2_terminal"
							name="l2_terminal"
							type="text"
							class="input w-full"
							value={editingReceta?.l2_terminal || ''}
						/>
					</div>

					<div>
						<label for="l3_terminal" class="block text-sm font-medium mb-2">L3 Terminal</label>
						<input
							id="l3_terminal"
							name="l3_terminal"
							type="text"
							class="input w-full"
							value={editingReceta?.l3_terminal || ''}
						/>
					</div>

					<div>
						<label for="l4_terminal" class="block text-sm font-medium mb-2">L4 Terminal</label>
						<input
							id="l4_terminal"
							name="l4_terminal"
							type="text"
							class="input w-full"
							value={editingReceta?.l4_terminal || ''}
						/>
					</div>

					<div>
						<label for="l5_terminal" class="block text-sm font-medium mb-2">L5 Terminal</label>
						<input
							id="l5_terminal"
							name="l5_terminal"
							type="text"
							class="input w-full"
							value={editingReceta?.l5_terminal || ''}
						/>
					</div>
				</div>

				<footer class="modal-footer flex justify-end gap-4">
					<button type="button" class="btn variant-ghost" onclick={closeModal}> Cancel </button>
					<button type="submit" class="btn variant-filled-primary">
						{editingReceta ? 'Update' : 'Create'}
					</button>
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

