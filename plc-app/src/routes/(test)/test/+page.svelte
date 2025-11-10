<script lang="ts">
	let data = $state<number[]>([]);
	let count = $state(0);

	let socket: WebSocket;

	$effect(() => {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const hostname = window.location.hostname;
		socket = new WebSocket(`${protocol}//${hostname}:4000`);

		socket.onmessage = (event) => {
			const msg = JSON.parse(event.data);
			if (msg.type === 'tcp-data') {
				data.push(...msg.payload);
				count += 1;
			}
		};

		socket.onopen = () => console.log('📡 Conectado al WebSocket');
		socket.onclose = () => console.log('❌ WebSocket cerrado');

		return () => socket.close();
	});
</script>

<h1>Dashboard de datos TCP</h1>
<h2>📦 Piezas escaneadas: {count}</h2>

{#if data.length}
	<ul>
		{#each data as byte, i}
			<li>[{i}] = {byte} → {byte.toString(2).padStart(8, '0')}</li>
		{/each}
	</ul>
{:else}
	<p>Esperando datos del PLC...</p>
{/if}
