import type { PageServerLoad, Actions } from './$types';
import { requirePermission } from '$lib/server/auth/guards';
import { prisma } from '$lib/prisma';
import { fail } from '@sveltejs/kit';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'management.roles.ver');

	const [roles, allPermisos] = await Promise.all([
		prisma.role.findMany({
			orderBy: {
				name: 'asc'
			},
			include: {
				permisosRol: {
					include: {
						permiso: true
					}
				},
				userRoles: {
					include: {
						user: {
							select: {
								username: true
							}
						}
					}
				}
			}
		}),
		prisma.permiso.findMany({
			orderBy: { key: 'asc' }
		})
	]);

	return {
		roles,
		allPermisos,
		user: event.locals.userWithPerms
	};
};

export const actions: Actions = {
	createRole: async (event) => {
		requirePermission(event, 'management.roles.crear');

		const formData = await event.request.formData();
		const name = formData.get('name') as string;
		const description = formData.get('description') as string;
		const permisoIds = formData.getAll('permisos') as string[];

		try {
			const role = await prisma.role.create({
				data: {
					name,
					description
				}
			});

			// Assign permissions
			for (const permisoId of permisoIds) {
				await prisma.permisoRol.create({
					data: {
						roleId: role.id,
						permisoId
					}
				});
			}

			return { success: true, message: 'Role created successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to create role. Name may already exist.' });
		}
	},

	updateRole: async (event) => {
		requirePermission(event, 'management.roles.editar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;
		const name = formData.get('name') as string;
		const description = formData.get('description') as string;

		try {
			await prisma.role.update({
				where: { id },
				data: {
					name,
					description
				}
			});

			return { success: true, message: 'Role updated successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to update role' });
		}
	},

	updatePermissions: async (event) => {
		requirePermission(event, 'management.roles.permisos');

		const formData = await event.request.formData();
		const roleId = formData.get('role_id') as string;
		const permisoIds = formData.getAll('permisos') as string[];

		try {
			// Remove all current permissions
			await prisma.permisoRol.deleteMany({
				where: { roleId }
			});

			// Add new permissions
			for (const permisoId of permisoIds) {
				await prisma.permisoRol.create({
					data: {
						roleId,
						permisoId
					}
				});
			}

			return { success: true, message: 'Role permissions updated successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to update role permissions' });
		}
	},

	deleteRole: async (event) => {
		requirePermission(event, 'management.roles.eliminar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;

		try {
			// Check if role has users
			const userCount = await prisma.userRole.count({
				where: { roleId: id }
			});

			if (userCount > 0) {
				return fail(400, {
					error: `Cannot delete role. It has ${userCount} assigned user(s).`
				});
			}

			await prisma.role.delete({
				where: { id }
			});

			return { success: true, message: 'Role deleted successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to delete role' });
		}
	}
};

