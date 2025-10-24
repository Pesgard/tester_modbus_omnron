<script lang="ts">
	import type { PageData } from './$types';
	import IconBook from '@lucide/svelte/icons/book';
	import IconBox from '@lucide/svelte/icons/box';
	import IconUsers from '@lucide/svelte/icons/users';
	import IconShield from '@lucide/svelte/icons/shield';

	let { data }: { data: PageData } = $props();

	function hasPermission(permission: string): boolean {
		if (!data.user?.permisos) return false;
		if (data.user.permisos.includes('*')) return true;
		if (data.user.permisos.includes(permission)) return true;
		const [namespace] = permission.split('.');
		return data.user.permisos.includes(`${namespace}.*`);
	}

	const sections = $derived([
		{
			title: 'Recipes',
			description: 'Manage cable recipes and specifications',
			href: '/dashboard/management/recetas',
			icon: IconBook,
			permission: 'management.recetas.ver'
		},
		{
			title: 'Lots',
			description: 'Create and manage production lots',
			href: '/dashboard/management/lotes',
			icon: IconBox,
			permission: 'management.lotes.ver'
		},
		{
			title: 'Users',
			description: 'Manage user accounts and access',
			href: '/dashboard/management/usuarios',
			icon: IconUsers,
			permission: 'management.usuarios.ver'
		},
		{
			title: 'Roles & Permissions',
			description: 'Configure roles and permissions',
			href: '/dashboard/management/roles',
			icon: IconShield,
			permission: 'management.roles.ver'
		}
	]);

	const visibleSections = $derived(sections.filter((section) => hasPermission(section.permission)));
</script>

<div class="management-page p-6 h-full overflow-auto">
	<div class="mb-8">
		<h1 class="text-3xl font-bold">Management</h1>
		<p class="text-surface-600-400 mt-1">
			Centralized administration for recipes, lots, users, and permissions
		</p>
	</div>

	<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
		{#each visibleSections as section}
			{@const Icon = section.icon}
			<a href={section.href} class="management-card card p-6 hover:shadow-lg transition-shadow">
				<div class="flex items-start gap-4">
					<div class="p-3 bg-primary-500/10 rounded-lg">
						<Icon class="size-8 text-primary-500" />
					</div>
					<div>
						<h2 class="text-xl font-bold mb-1">{section.title}</h2>
						<p class="text-sm text-surface-600-400">{section.description}</p>
					</div>
				</div>
			</a>
		{/each}
	</div>

	{#if visibleSections.length === 0}
		<div class="card p-12 text-center">
			<p class="text-surface-600-400">
				You don't have permission to access any management section.
			</p>
		</div>
	{/if}
</div>

<style>
	.management-card {
		cursor: pointer;
		border: 1px solid transparent;
	}

	.management-card:hover {
		border-color: var(--color-primary-500);
	}
</style>
