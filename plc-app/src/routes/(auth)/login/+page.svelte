<script lang="ts">
	import { enhance } from '$app/forms';
	import { CircleAlert, Eye, EyeOff, Factory, Lock, User } from '@lucide/svelte';
	import type { ActionData } from './$types';

	export let form: ActionData;

	let showPassword = false;

	const togglePasswordVisibility = () => {
		showPassword = !showPassword;
	};
</script>

<!-- Contenedor que ocupa toda la columna del grid -->
<div class="col-span-2 relative w-full h-full flex items-center justify-center bg-surface-50-950">
	<!-- Main Login Card -->
	<div class="card border border-surface-200-800 preset-filled-surface-100-900 p-10 shadow-2xl backdrop-blur-sm max-w-lg w-full mx-4">
		<!-- Header -->
		<header class="mb-8 text-center">
			<!-- Logo and Title -->
			<div class="mb-6 flex justify-center">
				<div class="rounded-full border border-primary-500/20 bg-primary-500/10 p-6">
					<Factory size={56} class="text-primary-500" />
				</div>
			</div>
			<h1 class="mb-3 h1 text-3xl font-bold">Iniciar Sesión</h1>
			<p class="text-base text-surface-400-600">Production Management System</p>
			<!-- Made by AxmeTech Watermark -->
			<p class="text-sm text-surface-400-600 mt-2">
				Made by <span class="text-primary-500 hover:underline">AxmeTech</span>
			</p>
		</header>

		<!-- Form -->
		<section class="p-2">
			<form method="post" use:enhance class="space-y-7">
				<label class="label">
					<span class="label-text text-left text-base font-medium mb-2">Username</span>
					<div class="input-group grid-cols-[auto_1fr]">
						<div class="ig-cell preset-tonal">
							<User size={20} />
						</div>
						<input
							type="text"
							name="username"
							class="ig-input text-lg py-5"
							placeholder="Enter your username"
							required
							autocomplete="username"
						/>
					</div>
				</label>

				<!-- Password Input -->
				<label class="label">
					<span class="label-text text-left text-base font-medium mb-2">Password</span>
					<div class="input-group grid-cols-[auto_1fr_auto]">
						<div class="ig-cell preset-tonal">
							<Lock size={20} />
						</div>
						<input
							type={showPassword ? 'text' : 'password'}
							name="password"
							class="ig-input text-lg py-5"
							placeholder="Enter your password"
							required
							autocomplete="current-password"
						/>
						<button
							type="button"
							class="ig-btn preset-tonal hover:preset-filled active:scale-95 transition-transform touch-manipulation min-w-[60px]"
							onclick={togglePasswordVisibility}
							aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
						>
							{#if showPassword}
								<EyeOff size={22} />
							{:else}
								<Eye size={22} />
							{/if}
						</button>
					</div>
				</label>

				{#if form?.error}
					<div
						class="alert flex items-center gap-3 rounded-container preset-filled-error-500 p-4 text-base"
						style="animation: shake 0.5s ease-in-out;"
					>
						<CircleAlert size={20} />
						<p>{form.error}</p>
					</div>
				{/if}

				<button
					type="submit"
					class="btn flex w-full items-center justify-center gap-3 preset-filled-primary-500 py-6 text-lg font-semibold active:scale-98 transition-transform touch-manipulation"
				>
					Login
				</button>
			</form>
		</section>
	</div>
</div>

<style>
	@keyframes shake {
		0%, 100% { transform: translateX(0); }
		10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
		20%, 40%, 60%, 80% { transform: translateX(5px); }
	}

	/* Estilos para mejorar la interacción táctil */
	:global(.ig-input) {
		touch-action: manipulation;
	}

	:global(.btn) {
		-webkit-tap-highlight-color: transparent;
	}

	.active\:scale-98:active {
		transform: scale(0.98);
	}

	.active\:scale-95:active {
		transform: scale(0.95);
	}
</style>