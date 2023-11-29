<script lang="ts">
    import Card from "$lib/components/Card.svelte";
    import { pb } from "$lib/pocketbase.js";

    export let data;
</script>

<div class="m-4">
    <Card title={data.show.title} classList="mx-auto max-w-5xl">
        <div class="rounded border-gray-100 m-2">
            {data.show.prompt}
        </div>
        <div class="rounded border-gray-100 m-2">
            {#each data.episodes as ep}
                <h2 class="text-lg font-bold">{ep.title}</h2>
                <!-- Responsive, flex-row on mobile -->
                <div class="flex w-full mb-4 flex-col lg:flex-row">
                    <div class="flex-1 mr-10">
                        <p class="text-sm text-gray-500 border-l-2 pl-2 border-gray-300">
                            {ep.summary}
                        </p>
                    </div>
                    <div class="flex">
                        <audio
                            controls
                            src={`${pb.baseUrl}/api/files/${ep.collectionId}/${ep.id}/${ep.audio_file}`}
                        ></audio>
                    </div>
                </div>
            {/each}
        </div>
    </Card>
</div>
