<script lang="ts">
    import { onMount } from "svelte";
    import { pb } from "./lib/pocketbase";

    // Get the attribute props from the parent component
    export let show;
    let shows: any[] = [];
    let episodes: any[] = [];

    onMount(async () => {
        episodes = (
            await pb.collection("episodes").getList(1, 100, {
                filter: `show.id = '${show.id}'`,
                sort: "show_index",
            })
        ).items;
    });
</script>

<div class="card">
    <h2>
        {show?.title}
    </h2>
    <a href="http://localhost:8090/pod/{show.id}" target="_blank" class="podcast-link">Podcast Link</a>

    <ul>
        <!-- Eps -->
        {#each episodes as ep}
            <li class="ep-well">
                <a href={`${pb.baseUrl}/api/files/${ep.collectionId}/${ep.id}/${ep.audio_file}`} target="_blank">▶️</a>
                {ep.title} — {ep.show_index}
                <blockquote>{ep.summary}</blockquote>
                <!-- Audio Element for on-site playing -->
                <audio controls preload="none" style="width: 100%">
                    <source
                        src={`${pb.baseUrl}/api/files/${ep.collectionId}/${ep.id}/${ep.audio_file}`}
                        type="audio/mpeg"
                    />
                    Your browser does not support the audio element.
                </audio>
            </li>
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

    .ep-well {
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .podcast-link {
        color: #fff;
        background: darkorange;
        padding: 0.5rem;
        border-radius: 4px;
        text-decoration: none;
        margin-left: 1rem;
    }
</style>
