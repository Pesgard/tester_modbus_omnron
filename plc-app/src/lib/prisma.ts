/**
 * @fileoverview This module initializes and exports a singleton instance of the PrismaClient
 * for interacting with the database. It ensures that the PrismaClient instance is reused
 * across hot module reloads in development mode to prevent multiple instances from being created.
 */

 /**
    * A global object to store the PrismaClient instance during development.
    * This prevents multiple instances of PrismaClient from being created during
    * hot module replacement (HMR) in development mode.
    */
 
 /**
    * The PrismaClient instance used for database interactions.
    * 
    * - In development mode, the instance is stored globally to ensure a single instance
    *   is reused across module reloads.
    * - In production mode, a new instance is created.
    * 
    * @constant
    * @type {PrismaClient}
    */
import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: ["query", "info", "warn", "error"]
  });

if (import.meta.env.DEV) {
  globalForPrisma.prisma = prisma;
}

export default prisma;