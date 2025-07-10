<script lang="ts">
	import { onMount } from 'svelte';
	// Skeleton UI Components
	import { AppBar, Tabs, Modal, Switch } from '@skeletonlabs/skeleton-svelte';
	// Lucide Icons
	import Settings from '@lucide/svelte/icons/settings';
	import Package from '@lucide/svelte/icons/package';
	import Users from '@lucide/svelte/icons/users';
	import Maximize from '@lucide/svelte/icons/maximize';
	import Minimize from '@lucide/svelte/icons/minimize';
	import Edit from '@lucide/svelte/icons/edit';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Plus from '@lucide/svelte/icons/plus';
	import Save from '@lucide/svelte/icons/save';
	import X from '@lucide/svelte/icons/x';

	// Types
	interface LackOrder {
		id: string;
		lackType: string;
		description: string;
		totalItemsNeeded: number;
		itemsProduced: number;
		status: 'open' | 'in_progress' | 'finished';
		priority: 'low' | 'medium' | 'high';
		department: string;
		productionLine: string;
		targetCompletionDate: Date;
		createdAt: Date;
		assignedTo?: string;
		estimatedHours: number;
	}

	interface User {
		id: string;
		name: string;
		email: string;
		role: 'admin' | 'manager' | 'operator' | 'viewer';
		isActive: boolean;
		createdAt: Date;
	}

	// State
	let activeTab = $state('orders');
	let isFullscreen = $state(false);
	let showOrderModal = $state(false);
	let showUserModal = $state(false);
	let editingOrder: LackOrder | null = $state(null);
	let editingUser: User | null = $state(null);

	// Sample data
	let orders = $state<LackOrder[]>([
		{
			id: '1',
			lackType: 'Gear Components Shortage',
			description: 'Critical shortage of precision gears for Assembly Line A',
			totalItemsNeeded: 150,
			itemsProduced: 0,
			status: 'open',
			priority: 'high',
			department: 'Manufacturing',
			productionLine: 'Line A',
			targetCompletionDate: new Date('2024-02-15'),
			createdAt: new Date('2024-01-15'),
			assignedTo: 'John Doe',
			estimatedHours: 24
		},
		{
			id: '2',
			lackType: 'Electronic Sensors Deficiency',
			description: 'Temperature sensors running low for quality control stations',
			totalItemsNeeded: 75,
			itemsProduced: 25,
			status: 'in_progress',
			priority: 'medium',
			department: 'Quality Control',
			productionLine: 'Line B',
			targetCompletionDate: new Date('2024-02-10'),
			createdAt: new Date('2024-01-14'),
			assignedTo: 'Jane Smith',
			estimatedHours: 16
		},
		{
			id: '3',
			lackType: 'Calibration Tools Missing',
			description: 'Precision measurement tools needed for equipment calibration',
			totalItemsNeeded: 20,
			itemsProduced: 20,
			status: 'finished',
			priority: 'low',
			department: 'Maintenance',
			productionLine: 'Line C',
			targetCompletionDate: new Date('2024-01-20'),
			createdAt: new Date('2024-01-10'),
			assignedTo: 'Mike Johnson',
			estimatedHours: 8
		}
	]);

	let users = $state<User[]>([
		{
			id: '1',
			name: 'John Doe',
			email: 'john.doe@company.com',
			role: 'admin',
			isActive: true,
			createdAt: new Date('2023-06-01')
		},
		{
			id: '2',
			name: 'Jane Smith',
			email: 'jane.smith@company.com',
			role: 'manager',
			isActive: true,
			createdAt: new Date('2023-07-15')
		},
		{
			id: '3',
			name: 'Mike Johnson',
			email: 'mike.johnson@company.com',
			role: 'operator',
			isActive: true,
			createdAt: new Date('2023-08-20')
		},
		{
			id: '4',
			name: 'Sarah Wilson',
			email: 'sarah.wilson@company.com',
			role: 'viewer',
			isActive: false,
			createdAt: new Date('2023-09-10')
		}
	]);

	// Form data
	let orderForm = $state({
		lackType: '',
		description: '',
		totalItemsNeeded: 0,
		itemsProduced: 0,
		status: 'open' as LackOrder['status'],
		priority: 'medium' as LackOrder['priority'],
		department: '',
		productionLine: '',
		targetCompletionDate: new Date(),
		assignedTo: '',
		estimatedHours: 0
	});

	let userForm = $state({
		name: '',
		email: '',
		role: 'viewer' as User['role'],
		isActive: true
	});

	// Functions
	function toggleFullscreen() {
		if (!document.fullscreenElement) {
			document.documentElement.requestFullscreen();
			isFullscreen = true;
		} else {
			document.exitFullscreen();
			isFullscreen = false;
		}
	}

	function openOrderModal(order?: LackOrder) {
		if (order) {
			editingOrder = order;
			orderForm = {
				lackType: order.lackType,
				description: order.description,
				totalItemsNeeded: order.totalItemsNeeded,
				itemsProduced: order.itemsProduced,
				status: order.status,
				priority: order.priority,
				department: order.department,
				productionLine: order.productionLine,
				targetCompletionDate: order.targetCompletionDate,
				assignedTo: order.assignedTo || '',
				estimatedHours: order.estimatedHours
			};
		} else {
			editingOrder = null;
			orderForm = {
				lackType: '',
				description: '',
				totalItemsNeeded: 0,
				itemsProduced: 0,
				status: 'open',
				priority: 'medium',
				department: '',
				productionLine: '',
				targetCompletionDate: new Date(),
				assignedTo: '',
				estimatedHours: 0
			};
		}
		showOrderModal = true;
	}

	function openUserModal(user?: User) {
		if (user) {
			editingUser = user;
			userForm = {
				name: user.name,
				email: user.email,
				role: user.role,
				isActive: user.isActive
			};
		} else {
			editingUser = null;
			userForm = {
				name: '',
				email: '',
				role: 'viewer',
				isActive: true
			};
		}
		showUserModal = true;
	}

	function saveOrder() {
		if (editingOrder) {
			// Update existing order
			const index = orders.findIndex(o => o.id === editingOrder!.id);
			if (index !== -1) {
				orders[index] = {
					...editingOrder,
					...orderForm
				};
			}
		} else {
			// Create new order
			const newOrder: LackOrder = {
				id: Date.now().toString(),
				...orderForm,
				createdAt: new Date()
			};
			orders.push(newOrder);
		}
		showOrderModal = false;
	}

	function saveUser() {
		if (editingUser) {
			// Update existing user
			const index = users.findIndex(u => u.id === editingUser!.id);
			if (index !== -1) {
				users[index] = {
					...editingUser,
					...userForm
				};
			}
		} else {
			// Create new user
			const newUser: User = {
				id: Date.now().toString(),
				...userForm,
				createdAt: new Date()
			};
			users.push(newUser);
		}
		showUserModal = false;
	}

	function deleteOrder(id: string) {
		orders = orders.filter(o => o.id !== id);
	}

	function deleteUser(id: string) {
		users = users.filter(u => u.id !== id);
	}

	function updateOrderStatus(id: string, status: LackOrder['status']) {
		const index = orders.findIndex(o => o.id === id);
		if (index !== -1) {
			orders[index].status = status;
		}
	}

	function getStatusColor(status: LackOrder['status']) {
		switch (status) {
			case 'open': return 'preset-filled-warning-500';
			case 'in_progress': return 'preset-filled-primary-500';
			case 'finished': return 'preset-filled-success-500';
			default: return 'preset-filled-surface-500';
		}
	}

	function getPriorityColor(priority: LackOrder['priority']) {
		switch (priority) {
			case 'high': return 'preset-filled-error-500';
			case 'medium': return 'preset-filled-warning-500';
			case 'low': return 'preset-filled-success-500';
			default: return 'preset-filled-surface-500';
		}
	}

	function getRoleColor(role: User['role']) {
		switch (role) {
			case 'admin': return 'preset-filled-error-500';
			case 'manager': return 'preset-filled-warning-500';
			case 'operator': return 'preset-filled-primary-500';
			case 'viewer': return 'preset-filled-surface-500';
			default: return 'preset-filled-surface-500';
		}
	}

	onMount(() => {
		// Listen for fullscreen changes
		document.addEventListener('fullscreenchange', () => {
			isFullscreen = !!document.fullscreenElement;
		});
	});
</script>

<div class="h-full flex flex-col">
	<!-- App Bar -->
	<AppBar>
		{#snippet lead()}
			<Settings size={24} />
		{/snippet}
		{#snippet trail()}
			<button 
				class="btn-icon preset-tonal" 
				onclick={toggleFullscreen}
				title={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
			>
				{#if isFullscreen}
					<Minimize size={20} />
				{:else}
					<Maximize size={20} />
				{/if}
			</button>
		{/snippet}
		{#snippet headline()}
			<h1 class="h1">Management</h1>
		{/snippet}
	</AppBar>

	<!-- Main Content -->
	<div class="flex-1 p-4">
		<Tabs value={activeTab} onValueChange={(e) => (activeTab = e.value)}>
			{#snippet list()}
				<Tabs.Control value="orders">
					{#snippet lead()}<Package size={20} />{/snippet}
					Order Management
				</Tabs.Control>
				<Tabs.Control value="users">
					{#snippet lead()}<Users size={20} />{/snippet}
					User Management
				</Tabs.Control>
			{/snippet}
			{#snippet content()}
				<!-- Orders Tab -->
				<Tabs.Panel value="orders">
					<div class="space-y-6">
						<!-- Orders Header -->
						<div class="flex justify-between items-center">
							<h2 class="h2">Lack Order Management</h2>
							<button class="btn preset-filled" onclick={() => openOrderModal()}>
								<Plus size={16} />
								<span>New Lack Order</span>
							</button>
						</div>

						<!-- Orders Table -->
						<div class="table-wrap">
							<table class="table">
								<thead>
									<tr>
										<th>Lack Type</th>
										<th>Progress</th>
										<th>Status</th>
										<th>Priority</th>
										<th>Department</th>
										<th>Target Date</th>
										<th>Actions</th>
									</tr>
								</thead>
								<tbody>
									{#each orders as order}
										<tr class="hover:preset-tonal">
											<td>
												<div class="space-y-2">
													<p class="font-bold text-sm">{order.lackType}</p>
													<p class="text-xs opacity-60 max-w-xs truncate">{order.description}</p>
													<p class="text-xs opacity-50">Assigned: {order.assignedTo || 'Unassigned'}</p>
												</div>
											</td>
											<td>
												<div class="space-y-1">
													<div class="flex justify-between text-xs">
														<span>{order.itemsProduced}</span>
														<span>{order.totalItemsNeeded}</span>
													</div>
													<div class="w-full bg-surface-300-600 rounded-full h-2">
														<div 
															class="bg-primary-500 h-2 rounded-full transition-all duration-300"
															style="width: {(order.itemsProduced / order.totalItemsNeeded) * 100}%"
														></div>
													</div>
													<p class="text-xs opacity-60 text-center">
														{Math.round((order.itemsProduced / order.totalItemsNeeded) * 100)}%
													</p>
												</div>
											</td>
											<td>
												<select 
													class="select max-w-32" 
													value={order.status}
													onchange={(e) => updateOrderStatus(order.id, e.currentTarget.value as LackOrder['status'])}
												>
													<option value="open">Open</option>
													<option value="in_progress">In Progress</option>
													<option value="finished">Finished</option>
												</select>
											</td>
											<td>
												<span class="badge {getPriorityColor(order.priority)} text-xs">
													{order.priority}
												</span>
											</td>
											<td>
												<div>
													<p class="font-medium">{order.department}</p>
													<p class="text-xs opacity-60">{order.assignedTo || 'Unassigned'}</p>
												</div>
											</td>
											<td>
												<div>
													<p class="text-sm">{order.targetCompletionDate.toLocaleDateString()}</p>
												</div>
											</td>
											<td>
												<div class="flex gap-2">
													<button 
														class="btn-icon btn-sm preset-tonal"
														onclick={() => openOrderModal(order)}
														title="Edit Lack Order"
													>
														<Edit size={14} />
													</button>
													<button 
														class="btn-icon btn-sm preset-tonal hover:preset-filled-error-500"
														onclick={() => deleteOrder(order.id)}
														title="Delete Lack Order"
													>
														<Trash2 size={14} />
													</button>
												</div>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>
				</Tabs.Panel>

				<!-- Users Tab -->
				<Tabs.Panel value="users">
					<div class="space-y-6">
						<!-- Users Header -->
						<div class="flex justify-between items-center">
							<h2 class="h2">User Management</h2>
							<button class="btn preset-filled" onclick={() => openUserModal()}>
								<Plus size={16} />
								<span>New User</span>
							</button>
						</div>

						<!-- Users Table -->
						<div class="table-wrap">
							<table class="table">
								<thead>
									<tr>
										<th>Name</th>
										<th>Email</th>
										<th>Role</th>
										<th>Status</th>
										<th>Created</th>
										<th>Actions</th>
									</tr>
								</thead>
								<tbody>
									{#each users as user}
										<tr class="hover:preset-tonal">
											<td class="font-bold">{user.name}</td>
											<td>{user.email}</td>
											<td>
												<span class="badge {getRoleColor(user.role)} text-xs">
													{user.role}
												</span>
											</td>
											<td>
												<span class="badge {user.isActive ? 'preset-filled-success-500' : 'preset-filled-surface-500'} text-xs">
													{user.isActive ? 'Active' : 'Inactive'}
												</span>
											</td>
											<td>{user.createdAt.toLocaleDateString()}</td>
											<td>
												<div class="flex gap-2">
													<button 
														class="btn-icon btn-sm preset-tonal"
														onclick={() => openUserModal(user)}
														title="Edit User"
													>
														<Edit size={14} />
													</button>
													<button 
														class="btn-icon btn-sm preset-tonal hover:preset-filled-error-500"
														onclick={() => deleteUser(user.id)}
														title="Delete User"
													>
														<Trash2 size={14} />
													</button>
												</div>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>
				</Tabs.Panel>
			{/snippet}
		</Tabs>
	</div>
</div>

<!-- Order Modal -->
<Modal
	open={showOrderModal}
	onOpenChange={(e) => (showOrderModal = e.open)}
	contentBase="card bg-surface-100-900 p-6 space-y-4 shadow-xl max-w-2xl"
	backdropClasses="backdrop-blur-sm"
>
	{#snippet content()}
		<header class="flex justify-between items-center">
			<h3 class="h3">{editingOrder ? 'Edit Order' : 'New Order'}</h3>
			<button 
				class="btn-icon preset-tonal" 
				onclick={() => (showOrderModal = false)}
			>
				<X size={16} />
			</button>
		</header>

		<form class="space-y-4">
			<label class="label">
				<span class="label-text">Lack Type</span>
				<input 
					class="input" 
					type="text" 
					bind:value={orderForm.lackType} 
					placeholder="Type of shortage/deficiency"
					required 
				/>
			</label>

			<label class="label">
				<span class="label-text">Description</span>
				<textarea 
					class="input" 
					bind:value={orderForm.description} 
					placeholder="Detailed description of the lack"
					rows="3"
				></textarea>
			</label>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<label class="label">
					<span class="label-text">Total Items Needed</span>
					<input 
						class="input" 
						type="number" 
						bind:value={orderForm.totalItemsNeeded} 
						placeholder="0"
						min="0"
						required 
					/>
				</label>

				<label class="label">
					<span class="label-text">Items Produced</span>
					<input 
						class="input" 
						type="number" 
						bind:value={orderForm.itemsProduced} 
						placeholder="0"
						min="0"
						max={orderForm.totalItemsNeeded}
					/>
				</label>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<label class="label">
					<span class="label-text">Department</span>
					<select class="select" bind:value={orderForm.department}>
						<option value="">Select Department</option>
						<option value="Manufacturing">Manufacturing</option>
						<option value="Quality Control">Quality Control</option>
						<option value="Maintenance">Maintenance</option>
						<option value="Assembly">Assembly</option>
						<option value="Packaging">Packaging</option>
					</select>
				</label>

				<label class="label">
					<span class="label-text">Production Line</span>
					<select class="select" bind:value={orderForm.productionLine}>
						<option value="">Select Line</option>
						<option value="Line A">Line A</option>
						<option value="Line B">Line B</option>
						<option value="Line C">Line C</option>
						<option value="Line D">Line D</option>
					</select>
				</label>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<label class="label">
					<span class="label-text">Status</span>
					<select class="select" bind:value={orderForm.status}>
						<option value="open">Open</option>
						<option value="in_progress">In Progress</option>
						<option value="finished">Finished</option>
					</select>
				</label>

				<label class="label">
					<span class="label-text">Priority</span>
					<select class="select" bind:value={orderForm.priority}>
						<option value="low">Low</option>
						<option value="medium">Medium</option>
						<option value="high">High</option>
					</select>
				</label>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<label class="label">
					<span class="label-text">Estimated Hours</span>
					<input 
						class="input" 
						type="number" 
						bind:value={orderForm.estimatedHours} 
						placeholder="0"
						min="0"
						step="0.5"
					/>
				</label>

				<label class="label">
					<span class="label-text">Target Completion Date</span>
					<input 
						class="input" 
						type="date" 
						value={orderForm.targetCompletionDate.toISOString().split('T')[0]}
						onchange={(e) => orderForm.targetCompletionDate = new Date(e.currentTarget.value)}
						required 
					/>
				</label>
			</div>

			<label class="label">
				<span class="label-text">Assigned To</span>
				<input 
					class="input" 
					type="text" 
					bind:value={orderForm.assignedTo} 
					placeholder="Assignee name"
				/>
			</label>
		</form>

		<footer class="flex justify-end gap-4">
			<button 
				type="button" 
				class="btn preset-tonal" 
				onclick={() => (showOrderModal = false)}
			>
				Cancel
			</button>
			<button 
				type="button" 
				class="btn preset-filled" 
				onclick={saveOrder}
			>
				<Save size={16} />
				<span>{editingOrder ? 'Update' : 'Create'}</span>
			</button>
		</footer>
	{/snippet}
</Modal>

<!-- User Modal -->
<Modal
	open={showUserModal}
	onOpenChange={(e) => (showUserModal = e.open)}
	contentBase="card bg-surface-100-900 p-6 space-y-4 shadow-xl max-w-2xl"
	backdropClasses="backdrop-blur-sm"
>
	{#snippet content()}
		<header class="flex justify-between items-center">
			<h3 class="h3">{editingUser ? 'Edit User' : 'New User'}</h3>
			<button 
				class="btn-icon preset-tonal" 
				onclick={() => (showUserModal = false)}
			>
				<X size={16} />
			</button>
		</header>

		<form class="space-y-4">
			<label class="label">
				<span class="label-text">Name</span>
				<input 
					class="input" 
					type="text" 
					bind:value={userForm.name} 
					placeholder="Full name"
					required 
				/>
			</label>

			<label class="label">
				<span class="label-text">Email</span>
				<input 
					class="input" 
					type="email" 
					bind:value={userForm.email} 
					placeholder="user@company.com"
					required 
				/>
			</label>

			<label class="label">
				<span class="label-text">Role</span>
				<select class="select" bind:value={userForm.role}>
					<option value="viewer">Viewer</option>
					<option value="operator">Operator</option>
					<option value="manager">Manager</option>
					<option value="admin">Admin</option>
				</select>
			</label>

			<div class="flex items-center gap-4">
				<span class="label-text">Active User</span>
				<Switch 
					checked={userForm.isActive} 
					onCheckedChange={(e) => (userForm.isActive = e.checked)} 
				/>
			</div>
		</form>

		<footer class="flex justify-end gap-4">
			<button 
				type="button" 
				class="btn preset-tonal" 
				onclick={() => (showUserModal = false)}
			>
				Cancel
			</button>
			<button 
				type="button" 
				class="btn preset-filled" 
				onclick={saveUser}
			>
				<Save size={16} />
				<span>{editingUser ? 'Update' : 'Create'}</span>
			</button>
		</footer>
	{/snippet}
</Modal>