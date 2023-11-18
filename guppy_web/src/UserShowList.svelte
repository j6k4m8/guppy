<script lang="ts">
      import { onMount, onDestroy } from 'svelte';
    import { currentUser, pb } from './lib/pocketbase';

    let shows: any[] = [];
    let showRequests: any[] = [];

    // currentUser.subscribe((user) => {
    //     // Refresh the list of shows when the user changes
    // });

    onMount(async () => {
        shows = (await pb.collection('shows').getList()).items;
        showRequests = (await pb.collection('show_requests').getList()).items;
    });


</script>

<h1>User Show List</h1>

{#if (showRequests.length + shows.length) > 0}
    <ul>
        {#each showRequests as showItem}
            <li>{showItem.title} —
                <!-- Loading spinner -->
                {#if showItem.status == "queued"}
                    <span>Queued</span>
                {:else if showItem.status == "creating"}
                    <span>creating</span>
                {:else if showItem.status == "errored"}
                    <span>errored</span>
                {/if}

            </li>
        {/each}
        {#each shows as showItem}
            <li>{showItem.title}</li>
        {/each}
    </ul>
{:else}
    <p>No shows found for the current user.</p>
{/if}
