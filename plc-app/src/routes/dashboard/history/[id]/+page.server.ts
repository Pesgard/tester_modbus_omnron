import type { PageServerLoad } from './$types';
import { requirePermission } from '$lib/server/auth/guards';
import { prisma } from '$lib/prisma';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'history.ver');

	const { id } = event.params;

	// Get lot with all related data
	const lote = await prisma.lote.findUnique({
		where: { id },
		include: {
			receta: true,
			creator: {
				select: {
					username: true
				}
			},
			piezas: {
				orderBy: {
					indice: 'desc'
				}
			},
			imagenes: {
				orderBy: {
					uploaded_at: 'desc'
				}
			},
			historial: {
				orderBy: {
					created_at: 'desc'
				},
				include: {
					user: {
						select: {
							username: true
						}
					}
				},
				take: 50
			}
		}
	});

	if (!lote) {
		error(404, 'Lot not found');
	}

	// Calculate statistics
	const total = lote.piezas_ok + lote.piezas_fallas;
	const accuracy = total > 0 ? (lote.piezas_ok / total) * 100 : 0;
	const defectRate = total > 0 ? (lote.piezas_fallas / total) * 100 : 0;

	// Group failures by type
	const failuresByType = lote.imagenes.reduce((acc: Record<string, number>, img) => {
		acc[img.tipo_falla] = (acc[img.tipo_falla] || 0) + 1;
		return acc;
	}, {});

	return {
		lote,
		stats: {
			total,
			accuracy,
			defectRate,
			failuresByType
		},
		user: event.locals.userWithPerms
	};
};

