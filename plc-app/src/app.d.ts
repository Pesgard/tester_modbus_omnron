// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		interface Locals {
			user: import("lucia").User | null;
			session: import("lucia").Session | null;
			userWithPerms: {
				id: string;
				username: string;
				roles: string[];
				permisos: string[];
			} | null;
		  }
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
