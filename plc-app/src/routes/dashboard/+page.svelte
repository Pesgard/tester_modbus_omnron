<script lang="ts">
    let { data } = $props();

    let user = $derived(data?.user);
    // $inspect(data);
</script>


<div>
    {#if data}
        <p>Welcome to the dashboard!</p>
        <p>Username: {user?.username}</p>
    {:else}
        <p>No data</p>
    {/if}
</div>