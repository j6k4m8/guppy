<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { currentUser, pb } from './lib/pocketbase';

    // Get the attribute props from the parent component
    export let show;
    let shows: any[] = [];
    let episodes: any[] = [];


    onMount(async () => {
        episodes = (await pb.collection('episodes').getList(1, 100, {
            filter: `show.id = '${show.id}'`
        })).items;
    });
</script>

<div class="card">
    <h2>
    {show?.title}
    </h2>

    <ul>
        <!-- Eps -->
        {#each episodes as ep}
            {ep.title} — {ep.show_index}
        {/each}
    </ul>
</div>

<style>
    ul {
        list-style: none;
        padding: 0;
    }

    .card {
        padding: 1rem;
        border: 1px solid #ccc;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
</style>