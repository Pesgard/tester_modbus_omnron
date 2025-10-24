import IconHome from '@lucide/svelte/icons/home';
import IconHistory from '@lucide/svelte/icons/history';
import IconFolderCog from '@lucide/svelte/icons/folder-cog';

export interface NavSection {
	id: string;
	label: string;
	href: string;
	permission: string;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	icon: any;
}

export const navSections: NavSection[] = [
	{
		id: 'production',
		label: 'Production',
		href: '/dashboard/production',
		permission: 'production.ver',
		icon: IconHome
	},
	{
		id: 'history',
		label: 'History',
		href: '/dashboard/history',
		permission: 'history.ver',
		icon: IconHistory
	},
	{
		id: 'management',
		label: 'Management',
		href: '/dashboard/management',
		permission: 'management.ver',
		icon: IconFolderCog
	}
];
