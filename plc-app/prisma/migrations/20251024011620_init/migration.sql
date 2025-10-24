-- CreateEnum
CREATE TYPE "public"."EstadoLote" AS ENUM ('OPEN', 'CLOSED', 'PAUSED');

-- CreateTable
CREATE TABLE "public"."User" (
    "id" TEXT NOT NULL,
    "username" TEXT NOT NULL,
    "hash_password" TEXT NOT NULL,
    "active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."Session" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Session_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."Role" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,

    CONSTRAINT "Role_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."Permiso" (
    "id" TEXT NOT NULL,
    "key" TEXT NOT NULL,
    "description" TEXT,

    CONSTRAINT "Permiso_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."PermisoRol" (
    "id" TEXT NOT NULL,
    "roleId" TEXT NOT NULL,
    "permisoId" TEXT NOT NULL,

    CONSTRAINT "PermisoRol_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."UserRole" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "roleId" TEXT NOT NULL,

    CONSTRAINT "UserRole_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."Receta" (
    "id" TEXT NOT NULL,
    "ppn" TEXT NOT NULL,
    "cable_np" TEXT NOT NULL,
    "quantity" DOUBLE PRECISION NOT NULL,
    "u_of_m" TEXT NOT NULL,
    "item_description" TEXT NOT NULL,
    "cantidad_conductores" INTEGER NOT NULL,
    "l1_terminal" TEXT,
    "l2_terminal" TEXT,
    "l3_terminal" TEXT,
    "l4_terminal" TEXT,
    "l5_terminal" TEXT,
    "activa" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Receta_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."Lote" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "receta_id" TEXT NOT NULL,
    "max_piezas_ok" INTEGER NOT NULL,
    "piezas_ok" INTEGER NOT NULL DEFAULT 0,
    "piezas_fallas" INTEGER NOT NULL DEFAULT 0,
    "estado" "public"."EstadoLote" NOT NULL DEFAULT 'OPEN',
    "started_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "closed_at" TIMESTAMP(3),
    "created_by" TEXT NOT NULL,

    CONSTRAINT "Lote_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."Pieza" (
    "id" TEXT NOT NULL,
    "lote_id" TEXT NOT NULL,
    "resultado_bits" JSONB NOT NULL,
    "ok" BOOLEAN NOT NULL,
    "indice" INTEGER NOT NULL,
    "imagen_path" TEXT NOT NULL,
    "processed_at" TIMESTAMP(3),
    "processed_by" TEXT,

    CONSTRAINT "Pieza_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."Imagen" (
    "id" TEXT NOT NULL,
    "pieza_id" TEXT NOT NULL,
    "path" TEXT NOT NULL,
    "thumbnail_path" TEXT NOT NULL,
    "uploaded_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Imagen_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."Historial" (
    "id" TEXT NOT NULL,
    "lote_id" TEXT NOT NULL,
    "pieza_id" TEXT,
    "user_id" TEXT NOT NULL,
    "action_key" TEXT NOT NULL,
    "meta" JSONB NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Historial_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_username_key" ON "public"."User"("username");

-- CreateIndex
CREATE UNIQUE INDEX "Role_name_key" ON "public"."Role"("name");

-- CreateIndex
CREATE UNIQUE INDEX "Permiso_key_key" ON "public"."Permiso"("key");

-- CreateIndex
CREATE UNIQUE INDEX "PermisoRol_roleId_permisoId_key" ON "public"."PermisoRol"("roleId", "permisoId");

-- CreateIndex
CREATE UNIQUE INDEX "UserRole_userId_roleId_key" ON "public"."UserRole"("userId", "roleId");

-- CreateIndex
CREATE UNIQUE INDEX "Receta_ppn_key" ON "public"."Receta"("ppn");

-- CreateIndex
CREATE UNIQUE INDEX "Lote_name_key" ON "public"."Lote"("name");

-- AddForeignKey
ALTER TABLE "public"."Session" ADD CONSTRAINT "Session_userId_fkey" FOREIGN KEY ("userId") REFERENCES "public"."User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."PermisoRol" ADD CONSTRAINT "PermisoRol_roleId_fkey" FOREIGN KEY ("roleId") REFERENCES "public"."Role"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."PermisoRol" ADD CONSTRAINT "PermisoRol_permisoId_fkey" FOREIGN KEY ("permisoId") REFERENCES "public"."Permiso"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."UserRole" ADD CONSTRAINT "UserRole_userId_fkey" FOREIGN KEY ("userId") REFERENCES "public"."User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."UserRole" ADD CONSTRAINT "UserRole_roleId_fkey" FOREIGN KEY ("roleId") REFERENCES "public"."Role"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."Lote" ADD CONSTRAINT "Lote_receta_id_fkey" FOREIGN KEY ("receta_id") REFERENCES "public"."Receta"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."Lote" ADD CONSTRAINT "Lote_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."Pieza" ADD CONSTRAINT "Pieza_lote_id_fkey" FOREIGN KEY ("lote_id") REFERENCES "public"."Lote"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."Pieza" ADD CONSTRAINT "Pieza_processed_by_fkey" FOREIGN KEY ("processed_by") REFERENCES "public"."User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."Imagen" ADD CONSTRAINT "Imagen_pieza_id_fkey" FOREIGN KEY ("pieza_id") REFERENCES "public"."Pieza"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."Historial" ADD CONSTRAINT "Historial_lote_id_fkey" FOREIGN KEY ("lote_id") REFERENCES "public"."Lote"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."Historial" ADD CONSTRAINT "Historial_pieza_id_fkey" FOREIGN KEY ("pieza_id") REFERENCES "public"."Pieza"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."Historial" ADD CONSTRAINT "Historial_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
