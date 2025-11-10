import type { PageServerLoad, Actions } from './$types';
import { requirePermission } from '$lib/server/auth/guards';
import { prisma } from '$lib/prisma';
import { fail, redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'management.recetas.ver');

	const recetas = await prisma.receta.findMany({
		orderBy: {
			ppn: 'asc'
		},
		include: {
			_count: {
				select: {
					lotes: true
				}
			}
		}
	});

	return {
		recetas,
		user: event.locals.userWithPerms
	};
};

export const actions: Actions = {
	create: async (event) => {
		requirePermission(event, 'management.recetas.crear');

		const formData = await event.request.formData();
		const data = {
			ppn: formData.get('ppn') as string,
			cable_np: formData.get('cable_np') as string,
			quantity: parseFloat(formData.get('quantity') as string),
			u_of_m: formData.get('u_of_m') as string,
			item_description: formData.get('item_description') as string,
			cantidad_conductores: parseInt(formData.get('cantidad_conductores') as string),
			l1_terminal: formData.get('l1_terminal') as string || null,
			l2_terminal: formData.get('l2_terminal') as string || null,
			l3_terminal: formData.get('l3_terminal') as string || null,
			l4_terminal: formData.get('l4_terminal') as string || null,
			l5_terminal: formData.get('l5_terminal') as string || null,
			activa: formData.get('activa') === 'on'
		};

		try {
			await prisma.receta.create({ data });
			return { success: true, message: 'Recipe created successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to create recipe' });
		}
	},

	update: async (event) => {
		requirePermission(event, 'management.recetas.editar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;

		const data = {
			ppn: formData.get('ppn') as string,
			cable_np: formData.get('cable_np') as string,
			quantity: parseFloat(formData.get('quantity') as string),
			u_of_m: formData.get('u_of_m') as string,
			item_description: formData.get('item_description') as string,
			cantidad_conductores: parseInt(formData.get('cantidad_conductores') as string),
			l1_terminal: formData.get('l1_terminal') as string || null,
			l2_terminal: formData.get('l2_terminal') as string || null,
			l3_terminal: formData.get('l3_terminal') as string || null,
			l4_terminal: formData.get('l4_terminal') as string || null,
			l5_terminal: formData.get('l5_terminal') as string || null,
			activa: formData.get('activa') === 'on'
		};

		try {
			await prisma.receta.update({
				where: { id },
				data
			});
			return { success: true, message: 'Recipe updated successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to update recipe' });
		}
	},

	delete: async (event) => {
		requirePermission(event, 'management.recetas.eliminar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;

		try {
			// Check if recipe has associated lots
			const loteCount = await prisma.lote.count({
				where: { receta_id: id }
			});

			if (loteCount > 0) {
				return fail(400, { 
					error: `Cannot delete recipe. It has ${loteCount} associated lot(s).` 
				});
			}

			await prisma.receta.delete({
				where: { id }
			});

			return { success: true, message: 'Recipe deleted successfully' };
		} catch (error) {
			return fail(400, { error: 'Failed to delete recipe' });
		}
	},

	toggle: async (event) => {
		requirePermission(event, 'management.recetas.activar');

		const formData = await event.request.formData();
		const id = formData.get('id') as string;
		const activa = formData.get('activa') === 'true';

		try {
			await prisma.receta.update({
				where: { id },
				data: { activa: !activa }
			});

			return { success: true, message: `Recipe ${!activa ? 'activated' : 'deactivated'}` };
		} catch (error) {
			return fail(400, { error: 'Failed to toggle recipe status' });
		}
	}
};

