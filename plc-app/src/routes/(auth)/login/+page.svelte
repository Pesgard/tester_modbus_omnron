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

<!-- Use Skeleton UI v3 for login page -->

<div class="relative w-full max-w-md">
	<!-- Nain Login Card -->
	<div
		class="card border border-surface-200-800 preset-filled-surface-100-900 p-8 shadow-2xl backdrop-blur-sm"
		style="transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);"
	>
		<!-- Header -->
		<header class="mb-6 text-center">
			<!-- Logo and Title -->
			<div class="mb-4 flex justify-center">
				<div class="rounded-full border border-primary-500/20 bg-primary-500/10 p-4">
					<Factory size={48} class="text-primary-500" />
				</div>
			</div>
			<h1 class="mb-2 h1 text-2xl font-bold">Iniciar Sesion</h1>
			<p class="tezt-sm text-surface-400-600">Production Managment System</p>
			<!-- Made by AxmeTech Watermark -->
			<p class="text-xs text-surface-400-600">
				Made by <span class="text-primary-500 hover:underline">AxmeTech </span>
			</p>

			<!-- Form -->
			<section class="p-4">
				<form method="post" use:enhance class="space-y-6">
					<label class="label">
						<span class="label-text text-left text-sm font-medium">Username</span>
						<div class="input-group grid-cols-[auto_1fr]">
							<div class="ig-cell preset-tonal">
								<User size={16} />
							</div>
							<input
								type="text"
								name="username"
								class=" ig-input"
								placeholder="Enter your username"
								required
							/>
						</div>
					</label>

					<!-- Password Input -->
					<label class="label">
						<span class="label-text text-left text-sm font-medium">Password</span>
						<div class="input-group grid-cols-[auto_1fr]">
							<div class="ig-cell preset-tonal">
								<Lock size={16} />
							</div>
							<input
								type={showPassword ? 'text' : 'password'}
								name="password"
								class="ig-input"
								placeholder="Enter your password"
								required
							/>
							<button
								type="button"
								class="ig-btn preset-tonal hover:preset-filled"
								onclick={togglePasswordVisibility}
							>
								<!-- Toggle password visibility -->
								{#if showPassword}
									<EyeOff size={16} />
								{:else}
									<Eye size={16} />
								{/if}
							</button>
						</div>
					</label>

					{#if form?.error}
						<div
							class="alert mb-6 flex items-center gap-2 rounded-container preset-filled-error-500 p-3 text-sm"
							style="animation: shake 0.5s ease-in-out;"
						>
							<CircleAlert size={16} />
							<p>{form.error}</p>
						</div>
					{/if}

					<button
						type="submit"
						class="btn flex w-full items-center justify-center gap-2 preset-filled-primary-500 py-3"
					>
						Login
					</button>
				</form>
			</section>
		</header>
	</div>
</div>
