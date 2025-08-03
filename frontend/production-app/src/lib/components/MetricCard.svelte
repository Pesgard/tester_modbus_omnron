<script lang="ts">
	interface Props {
		title: string;
		value: string | number;
		icon: string;
		valueClass?: string;
		subtitle?: string;
	}

	let { title, value, icon, valueClass = '', subtitle = '' }: Props = $props();
</script>

<div class="card preset-outlined p-4 hover:shadow-lg transition-shadow">
	<div class="flex items-center justify-between">
		<div class="flex-1">
			<p class="text-sm text-surface-600-400 font-medium">{title}</p>
			<p class="text-2xl font-bold {valueClass} break-words">
				{typeof value === 'number' ? value.toLocaleString() : value}
			</p>
			{#if subtitle}
				<p class="text-xs text-surface-500-400 mt-1">{subtitle}</p>
			{/if}
		</div>
		<div class="text-3xl ml-4 flex-shrink-0">{icon}</div>
	</div>
</div>