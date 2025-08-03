<script lang="ts">
	import { productionStore } from '$lib/stores/production';
	import { getWebSocketInstance } from '$lib/services/websocket';

	function handleReconnect() {
		const ws = getWebSocketInstance();
		ws.connect();
	}
</script>

<div class="flex items-center space-x-2">
	{#if $productionStore.connectionStatus === 'connected'}
		<div class="w-3 h-3 bg-success-500 rounded-full animate-pulse"></div>
		<span class="text-sm text-success-500 font-medium">Connected</span>
	{:else if $productionStore.connectionStatus === 'connecting'}
		<div class="w-3 h-3 bg-warning-500 rounded-full animate-pulse"></div>
		<span class="text-sm text-warning-500 font-medium">Connecting...</span>
	{:else}
		<div class="w-3 h-3 bg-error-500 rounded-full"></div>
		<span class="text-sm text-error-500 font-medium">Disconnected</span>
		<button 
			class="btn preset-tonal-primary btn-sm ml-2"
			onclick={handleReconnect}
		>
			🔄 Reconnect
		</button>
	{/if}
</div>