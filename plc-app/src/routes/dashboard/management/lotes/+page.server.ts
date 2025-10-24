import type { PageServerLoad, Actions } from './$types';
import { requirePermission } from '$lib/server/auth/guards';
import { prisma } from '$lib/prisma';
import { fail } from '@sveltejs/kit';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'management.lotes.ver');

	const [lotes, recetas] = await Promise.all([
		prisma.lote.findMany({
			orderBy: {
				started_at: 'desc'
			},
			include: {
				receta: true,
				creator: {
					select: {
						username: true
					}
				},
				_count: {
					select: {
						piezas: true
					}
				}
			}
		}),
		prisma.receta.findMany({
			where: { activa: true },
			orderBy: { ppn: 'asc' }
		})
	]);

	return {
		lotes,
		recetas,
		user: event.locals.userWithPerms
	};
};

export const actions: Actions = {
	create: async (event) => {
		requirePermission(event, 'management.lotes.crear');

		const formData = await event.request.formData();
		const data = {
			name: formData.get('name') as string,
			receta_id: formData.get('receta_id') as string,
			max_piezas_ok: parseInt(formData.get('max_piezas_ok') as string),
			created_by: event.locals.user!.id,
			estado: 'OPEN' as const
		};

		try {
			await prisma.lote.create({ data });
			return { success: true, message: 'Lot created successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to create lot' });
		}
	},

	update: async (event) => {
		requirePermission(event, 'management.lotes.editar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;

		const data = {
			name: formData.get('name') as string,
			max_piezas_ok: parseInt(formData.get('max_piezas_ok') as string)
		};

		try {
			await prisma.lote.update({
				where: { id },
				data
			});
			return { success: true, message: 'Lot updated successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to update lot' });
		}
	},

	close: async (event) => {
		requirePermission(event, 'management.lotes.cerrar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;

		try {
			await prisma.lote.update({
				where: { id },
				data: {
					estado: 'CLOSED',
					closed_at: new Date()
				}
			});
			return { success: true, message: 'Lot closed successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to close lot' });
		}
	},

	reopen: async (event) => {
		requirePermission(event, 'management.lotes.reabrir');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;

		try {
			await prisma.lote.update({
				where: { id },
				data: {
					estado: 'OPEN',
					closed_at: null
				}
			});
			return { success: true, message: 'Lot reopened successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to reopen lot' });
		}
	},

	pause: async (event) => {
		requirePermission(event, 'management.lotes.pausar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;

		try {
			await prisma.lote.update({
				where: { id },
				data: { estado: 'PAUSED' }
			});
			return { success: true, message: 'Lot paused successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to pause lot' });
		}
	},

	resume: async (event) => {
		requirePermission(event, 'management.lotes.reanudar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;

		try {
			await prisma.lote.update({
				where: { id },
				data: { estado: 'OPEN' }
			});
			return { success: true, message: 'Lot resumed successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to resume lot' });
		}
	},

	delete: async (event) => {
		requirePermission(event, 'management.lotes.eliminar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;

		try {
			// Check if lot has pieces
			const pieceCount = await prisma.pieza.count({
				where: { lote_id: id }
			});

			if (pieceCount > 0) {
				return fail(400, {
					error: `Cannot delete lot. It has ${pieceCount} piece(s). Close it instead.`
				});
			}

			await prisma.lote.delete({
				where: { id }
			});

			return { success: true, message: 'Lot deleted successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to delete lot' });
		}
	}
};

