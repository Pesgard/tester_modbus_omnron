import type { PageServerLoad } from './$types';
import { prisma } from '$lib/prisma';

export const load: PageServerLoad = async ({ locals }) => {
    // Obtener estadísticas generales del sistema
    const [
        totalRecetas,
        totalLotes,
        lotesActivos,
        totalPiezasOK,
        totalPiezasNOK,
        ultimosLotes
    ] = await Promise.all([
        // Total de recetas activas
        prisma.receta.count({ where: { activa: true } }),
        
        // Total de lotes
        prisma.lote.count(),
        
        // Lotes activos (OPEN o PAUSED)
        prisma.lote.count({ where: { estado: { in: ['OPEN', 'PAUSED'] } } }),
        
        // Total de piezas OK
        prisma.lote.aggregate({
            _sum: { piezas_ok: true }
        }),
        
        // Total de piezas NOK
        prisma.lote.aggregate({
            _sum: { piezas_fallas: true }
        }),
        
        // Últimos 5 lotes
        prisma.lote.findMany({
            take: 5,
            orderBy: { started_at: 'desc' },
            include: {
                receta: {
                    select: {
                        ppn: true,
                        item_description: true
                    }
                },
                creator: {
                    select: {
                        username: true
                    }
                }
            }
        })
    ]);

    const totalPiezas = (totalPiezasOK._sum.piezas_ok || 0) + (totalPiezasNOK._sum.piezas_fallas || 0);
    const precisión = totalPiezas > 0 
        ? ((totalPiezasOK._sum.piezas_ok || 0) / totalPiezas * 100).toFixed(1)
        : '0.0';

    return {
        stats: {
            totalRecetas,
            totalLotes,
            lotesActivos,
            totalPiezasOK: totalPiezasOK._sum.piezas_ok || 0,
            totalPiezasNOK: totalPiezasNOK._sum.piezas_fallas || 0,
            totalPiezas,
            precisión
        },
        ultimosLotes,
        user: locals.userWithPerms
    };
};