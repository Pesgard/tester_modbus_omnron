<script lang="ts">
	import type { PageData, ActionData } from './$types';
	import { enhance } from '$app/forms';
	import IconPlus from '@lucide/svelte/icons/plus';
	import IconEdit from '@lucide/svelte/icons/edit';
	import IconTrash from '@lucide/svelte/icons/trash';
	import IconLock from '@lucide/svelte/icons/lock';
	import IconUnlock from '@lucide/svelte/icons/unlock';
	import IconPause from '@lucide/svelte/icons/pause';
	import IconPlay from '@lucide/svelte/icons/play';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	let showModal = $state(false);
	let editingLote = $state<any>(null);
	let searchQuery = $state('');
	let statusFilter = $state<'all' | 'OPEN' | 'CLOSED' | 'PAUSED'>('all');

	const filteredLotes = $derived(
		data.lotes.filter((lote) => {
			const matchesSearch =
				lote.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
				lote.receta.ppn.toLowerCase().includes(searchQuery.toLowerCase());
			const matchesStatus = statusFilter === 'all' || lote.estado === statusFilter;
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

	const canCreate = $derived(hasPermission('management.lotes.crear'));
	const canEdit = $derived(hasPermission('management.lotes.editar'));
	const canDelete = $derived(hasPermission('management.lotes.eliminar'));
	const canClose = $derived(hasPermission('management.lotes.cerrar'));
	const canReopen = $derived(hasPermission('management.lotes.reabrir'));
	const canPause = $derived(hasPermission('management.lotes.pausar'));
	const canResume = $derived(hasPermission('management.lotes.reanudar'));

	function openCreateModal() {
		editingLote = null;
		showModal = true;
	}

	function openEditModal(lote: any) {
		editingLote = lote;
		showModal = true;
	}

	function closeModal() {
		showModal = false;
		editingLote = null;
	}

	function generateLotName() {
		const date = new Date().toISOString().slice(0, 10);
		const random = Math.floor(Math.random() * 1000)
			.toString()
			.padStart(3, '0');
		return `LOTE-${random}-${date}`;
	}
</script>

<div class="lotes-page p-6 h-full overflow-auto">
	<div class="flex items-center justify-between mb-6">
		<div>
			<h1 class="text-3xl font-bold">Lots Management</h1>
			<p class="text-surface-600-400 mt-1">Create and manage production lots</p>
		</div>
		{#if canCreate}
			<button class="btn variant-filled-primary" onclick={openCreateModal}>
				<IconPlus size={20} />
				<span>New Lot</span>
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
				placeholder="Search by lot name or PPN..."
				bind:value={searchQuery}
			/>
			<select class="select" bind:value={statusFilter}>
				<option value="all">All Status</option>
				<option value="OPEN">Open</option>
				<option value="CLOSED">Closed</option>
				<option value="PAUSED">Paused</option>
			</select>
		</div>
	</div>

	<!-- Lots Table -->
	<div class="card variant-glass-surface p-6">
		<div class="table-container">
			<table class="table table-hover">
				<thead>
					<tr>
						<th>Lot Name</th>
						<th>Recipe (PPN)</th>
						<th>Status</th>
						<th>OK / Target</th>
						<th>NOK</th>
						<th>Progress</th>
						<th>Created By</th>
						<th>Started</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each filteredLotes as lote}
						{@const progress = (lote.piezas_ok / lote.max_piezas_ok) * 100}
						<tr>
							<td class="font-semibold">{lote.name}</td>
							<td>
								<div class="font-mono text-sm">{lote.receta.ppn}</div>
								<div class="text-xs text-surface-600-400">
									{lote.receta.item_description.slice(0, 40)}...
								</div>
							</td>
							<td>
								<span
									class="badge"
									class:variant-filled-success={lote.estado === 'OPEN'}
									class:variant-filled-error={lote.estado === 'CLOSED'}
									class:variant-filled-warning={lote.estado === 'PAUSED'}
								>
									{lote.estado}
								</span>
							</td>
							<td class="text-success-500 font-semibold">
								{lote.piezas_ok} / {lote.max_piezas_ok}
							</td>
							<td class="text-error-500 font-semibold">{lote.piezas_fallas}</td>
							<td>
								<div class="flex items-center gap-2">
									<div class="flex-1">
										<div class="progress-bar h-2 bg-surface-200-800 rounded-full overflow-hidden">
											<div class="progress-fill h-full bg-success-500 transition-all" style="width: {progress}%"></div>
										</div>
									</div>
									<span class="text-sm text-surface-600-400 min-w-[3ch]">{progress.toFixed(0)}%</span>
								</div>
							</td>
							<td>{lote.creator.username}</td>
							<td class="text-sm">{new Date(lote.started_at).toLocaleDateString()}</td>
							<td>
								<div class="flex gap-1">
									{#if lote.estado === 'OPEN' && canPause}
										<form method="POST" action="?/pause" use:enhance>
											<input type="hidden" name="id" value={lote.id} />
											<button type="submit" class="btn btn-sm variant-ghost" title="Pause">
												<IconPause size={16} />
											</button>
										</form>
									{/if}

									{#if lote.estado === 'PAUSED' && canResume}
										<form method="POST" action="?/resume" use:enhance>
											<input type="hidden" name="id" value={lote.id} />
											<button type="submit" class="btn btn-sm variant-ghost" title="Resume">
												<IconPlay size={16} />
											</button>
										</form>
									{/if}

									{#if lote.estado === 'OPEN' && canClose}
										<form method="POST" action="?/close" use:enhance>
											<input type="hidden" name="id" value={lote.id} />
											<button type="submit" class="btn btn-sm variant-ghost" title="Close">
												<IconLock size={16} />
											</button>
										</form>
									{/if}

									{#if lote.estado === 'CLOSED' && canReopen}
										<form method="POST" action="?/reopen" use:enhance>
											<input type="hidden" name="id" value={lote.id} />
											<button type="submit" class="btn btn-sm variant-ghost" title="Reopen">
												<IconUnlock size={16} />
											</button>
										</form>
									{/if}

									{#if lote.estado !== 'OPEN' && canEdit}
										<button
											class="btn btn-sm variant-ghost"
											onclick={() => openEditModal(lote)}
											title="Edit"
										>
											<IconEdit size={16} />
										</button>
									{/if}

									{#if lote._count.piezas === 0 && canDelete}
										<form method="POST" action="?/delete" use:enhance>
											<input type="hidden" name="id" value={lote.id} />
											<button
												type="submit"
												class="btn btn-sm variant-ghost-error"
												title="Delete"
												onclick={(e) => {
													if (!confirm('Are you sure you want to delete this lot?')) {
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

			{#if filteredLotes.length === 0}
				<div class="text-center py-12 text-surface-600-400">No lots found</div>
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
				<h2 class="h2">{editingLote ? 'Edit Lot' : 'Create New Lot'}</h2>
			</header>

			<form
				method="POST"
				action={editingLote ? '?/update' : '?/create'}
				use:enhance={() => {
					return async ({ result }) => {
						if (result.type === 'success') {
							closeModal();
						}
					};
				}}
			>
				{#if editingLote}
					<input type="hidden" name="id" value={editingLote.id} />
				{/if}

				<div class="space-y-4">
					<div>
						<label class="label">
							<span>Lot Name *</span>
							<div class="input-group input-group-divider grid-cols-[1fr_auto]">
								<input
									name="name"
									type="text"
									class="input"
									value={editingLote?.name || ''}
									placeholder="LOTE-001-2025-01-24"
									required
								/>
								{#if !editingLote}
									<button
										type="button"
										class="btn variant-ghost-surface"
										onclick={(e) => {
											const form = e.currentTarget.closest('form');
											const input = form?.querySelector('input[name="name"]') as HTMLInputElement;
											if (input) input.value = generateLotName();
										}}
									>
										Generate
									</button>
								{/if}
							</div>
						</label>
					</div>

					{#if !editingLote}
						<label class="label">
							<span>Recipe *</span>
							<select name="receta_id" class="select" required>
								<option value="">Select a recipe</option>
								{#each data.recetas as receta}
									<option value={receta.id}>
										{receta.ppn} - {receta.item_description.slice(0, 60)}
									</option>
								{/each}
							</select>
						</label>
					{/if}

					<label class="label">
						<span>Target (OK Pieces) *</span>
						<input
							name="max_piezas_ok"
							type="number"
							min="1"
							class="input"
							value={editingLote?.max_piezas_ok || 100}
							required
						/>
					</label>
				</div>

				<footer class="modal-footer flex justify-end gap-4">
					<button type="button" class="btn variant-ghost" onclick={closeModal}> Cancel </button>
					<button type="submit" class="btn variant-filled-primary">
						{editingLote ? 'Update' : 'Create'}
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
