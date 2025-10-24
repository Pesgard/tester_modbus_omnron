import type { PageServerLoad, Actions } from './$types';
import { requirePermission } from '$lib/server/auth/guards';
import { prisma } from '$lib/prisma';
import { fail } from '@sveltejs/kit';
import { Argon2id } from 'oslo/password';
import crypto from 'crypto';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'management.usuarios.ver');

	const [users, roles] = await Promise.all([
		prisma.user.findMany({
			orderBy: {
				username: 'asc'
			},
			include: {
				roles: {
					include: {
						role: true
					}
				}
			}
		}),
		prisma.role.findMany({
			orderBy: { name: 'asc' }
		})
	]);

	return {
		users,
		roles,
		user: event.locals.userWithPerms
	};
};

export const actions: Actions = {
	create: async (event) => {
		requirePermission(event, 'management.usuarios.crear');

		const formData = await event.request.formData();
		const username = formData.get('username') as string;
		const password = formData.get('password') as string;
		const roleIds = formData.getAll('roles') as string[];
		const active = formData.get('active') === 'on';

		try {
			const hashedPassword = await new Argon2id().hash(password);

			const user = await prisma.user.create({
				data: {
					id: crypto.randomUUID(),
					username,
					hash_password: hashedPassword,
					active
				}
			});

			// Assign roles
			for (const roleId of roleIds) {
				await prisma.userRole.create({
					data: {
						userId: user.id,
						roleId
					}
				});
			}

			return { success: true, message: 'User created successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to create user. Username may already exist.' });
		}
	},

	update: async (event) => {
		requirePermission(event, 'management.usuarios.editar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;
		const username = formData.get('username') as string;
		const active = formData.get('active') === 'on';

		try {
			await prisma.user.update({
				where: { id },
				data: {
					username,
					active
				}
			});

			return { success: true, message: 'User updated successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to update user' });
		}
	},

	changePassword: async (event) => {
		requirePermission(event, 'management.usuarios.password');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;
		const newPassword = formData.get('new_password') as string;

		try {
			const hashedPassword = await new Argon2id().hash(newPassword);

			await prisma.user.update({
				where: { id },
				data: {
					hash_password: hashedPassword
				}
			});

			return { success: true, message: 'Password changed successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to change password' });
		}
	},

	updateRoles: async (event) => {
		requirePermission(event, 'management.usuarios.roles');

		const formData = await event.request.formData();
		const userId = formData.get('user_id') as string;
		const roleIds = formData.getAll('roles') as string[];

		try {
			// Remove all current roles
			await prisma.userRole.deleteMany({
				where: { userId }
			});

			// Add new roles
			for (const roleId of roleIds) {
				await prisma.userRole.create({
					data: {
						userId,
						roleId
					}
				});
			}

			return { success: true, message: 'User roles updated successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to update user roles' });
		}
	},

	toggle: async (event) => {
		requirePermission(event, 'management.usuarios.activar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;
		const active = formData.get('active') === 'true';

		try {
			await prisma.user.update({
				where: { id },
				data: { active: !active }
			});

			return { success: true, message: `User ${!active ? 'activated' : 'deactivated'}` };
		} catch (error) {
			return fail(400, { error: 'Failed to toggle user status' });
		}
	},

	delete: async (event) => {
		requirePermission(event, 'management.usuarios.eliminar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;

		// Prevent deleting current user
		if (id === event.locals.user?.id) {
			return fail(400, { error: 'Cannot delete your own user account' });
		}

		try {
			await prisma.user.delete({
				where: { id }
			});

			return { success: true, message: 'User deleted successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to delete user' });
		}
	}
};

