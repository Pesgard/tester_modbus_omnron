/*
  Warnings:

  - Added the required column `lote_id` to the `Imagen` table without a default value. This is not possible if the table is not empty.
  - Added the required column `tipo_falla` to the `Imagen` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "public"."Imagen" DROP CONSTRAINT "Imagen_pieza_id_fkey";

-- AlterTable
ALTER TABLE "public"."Imagen" ADD COLUMN     "lote_id" TEXT NOT NULL,
ADD COLUMN     "metadata" JSONB,
ADD COLUMN     "tipo_falla" TEXT NOT NULL,
ALTER COLUMN "pieza_id" DROP NOT NULL,
ALTER COLUMN "thumbnail_path" SET DEFAULT '';

-- AddForeignKey
ALTER TABLE "public"."Imagen" ADD CONSTRAINT "Imagen_lote_id_fkey" FOREIGN KEY ("lote_id") REFERENCES "public"."Lote"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."Imagen" ADD CONSTRAINT "Imagen_pieza_id_fkey" FOREIGN KEY ("pieza_id") REFERENCES "public"."Pieza"("id") ON DELETE SET NULL ON UPDATE CASCADE;
