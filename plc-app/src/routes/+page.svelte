<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    // Esta página solo se mostrará brevemente antes del redirect
    // El redirect principal se maneja en +page.server.ts
    onMount(() => {
        // Fallback en caso de que el server-side redirect falle
        // Esto normalmente no debería ejecutarse
        goto('/login', { replaceState: true });
    });
</script>

<!-- Loading state mientras se procesa el redirect -->
<div class="flex min-h-screen w-full items-center justify-center bg-gradient-to-br from-surface-50 to-surface-200 dark:from-surface-900 dark:to-surface-800">
    <div class="text-center">
        <div class="mb-4 flex justify-center">
            <div class="variant-filled-primary rounded-full p-4">
                <svg class="animate-spin h-8 w-8" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            </div>
        </div>
        <h2 class="h3 mb-2">Cargando...</h2>
        <p class="text-surface-500-400">Redirigiendo al sistema</p>
    </div>
</div>