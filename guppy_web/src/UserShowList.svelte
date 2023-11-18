<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { currentUser, pb } from "./lib/pocketbase";
    import NewShowPrompt from "./NewShowPrompt.svelte";
    import ShowDetails from "./ShowDetails.svelte";

    let shows: any[] = [];
    let showRequests: any[] = [];
    let selectedShow: any = null;

    // currentUser.subscribe((user) => {
    //     // Refresh the list of shows when the user changes
    // });

    onMount(async () => {
        shows = (await pb.collection("shows").getList()).items;
        showRequests = (await pb.collection("show_requests").getList()).items;
    });
</script>

<div class="container">
    <div class="row">
        <div class="column">
            <h1>User Show List</h1>

            <NewShowPrompt />
            <hr />

            <h2>my shows</h2>

            {#if showRequests.length + shows.length > 0}
                <ul>
                    {#each showRequests as showItem}
                        <li>
                            <button on:click={() => {}}>
                                {showItem.title} —
                                <!-- Loading spinner -->
                                {#if showItem.status == "queued"}
                                    <span>Queued</span>
                                {:else if showItem.status == "creating"}
                                    <span>creating</span>
                                {:else if showItem.status == "errored"}
                                    <span>errored</span>
                                {/if}
                            </button>
                        </li>
                    {/each}
                    {#each shows as showItem}
                        <li>
                            <button on:click={() => (selectedShow = showItem)}>
                                {showItem.title}
                            </button>
                        </li>
                    {/each}
                </ul>
            {:else}
                <p>No shows found for the current user.</p>
            {/if}
        </div>

        <div class="column">
            {#if selectedShow}
                <ShowDetails show={selectedShow} />
            {/if}
        </div>
    </div>
</div>

<style>
    li {
        list-style: none;
        padding: 0;
    }

    .container {
        padding: 1em;
    }
</style>
