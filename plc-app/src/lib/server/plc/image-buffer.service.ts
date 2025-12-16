import type { PrismaClient } from '@prisma/client';

export class ImageBufferService {
	constructor(private prisma: PrismaClient) {}

	async savePendingImage(data: {
		timestamp: Date;
		filename: string;
		finalPath: string;
		size: number;
	}) {
		return this.prisma.pendingImage.create({
			data
		});
	}

	async findImagesForTimestamp(ts: Date, limit = 3, windowMs = 60000) {
		// windowMs: 60000 = 1 minute (search window: ±1 minute from timestamp)
		const pivot = ts.getTime();
		const gte = new Date(pivot - windowMs);
		const lte = new Date(pivot + windowMs);

		return this.prisma.pendingImage.findMany({
			where: {
				linked: false,
				timestamp: {
					gte,
					lte
				}
			},
			orderBy: {
				timestamp: 'asc'
			},
			take: limit
		});
	}

	async markAsLinked(ids: string[], pieceId: string) {
		if (!ids.length) return { count: 0 };

		return this.prisma.pendingImage.updateMany({
			where: { id: { in: ids } },
			data: {
				linked: true,
				linkedPieceId: pieceId,
				linkedAt: new Date()
			}
		});
	}
}

import { prisma } from '$lib/prisma';

export const imageBufferService = new ImageBufferService(prisma);
