<script lang="ts">
    import Card from "$lib/components/Card.svelte";

    import { onMount } from "svelte";
    import { pb, currentUser } from "$lib/pocketbase";

    let shows: any[] = [];
    let showRequests: any[] = [];
    let selectedShow: any = null;

    let newShowTitle: string = "";
    let newShowPrompt: string = "";

    async function createShow() {
        try {
            await pb.collection("show_requests").create({
                title: newShowTitle,
                prompt: newShowPrompt,
                creator: $currentUser.id,
                status: "queued"
            });
        } catch (e) {
            console.error(e);
        }
        newShowTitle = "";
        newShowPrompt = "";
    }

    onMount(async () => {
        shows = (await pb.collection("shows").getList()).items.map((show) => {
            show.createdDate = new Date(show.created);
            return show;
        });
        showRequests = (await pb.collection("show_requests").getList()).items;
    });
</script>

<div class="flex flex-row">
    <div class="m-4 flex-1">
        <Card title="My Shows" classList="mx-auto max-w-5xl">
            {#each showRequests as showItem}
                <div
                    class="flex flex-row justify-between hover:bg-gray-100 whitespace-nowrap w-full mb-3 align-middle"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke-width="1.5"
                        stroke="currentColor"
                        class="w-5 h-5 mr-2 bg-orange-200 rounded p-1 animate-pulse"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3l-3 3"
                        />
                    </svg>
                    <span class="flex-1">
                        {showItem.title}
                    </span>
                    <!-- Loading spinner -->
                    {#if showItem.status == "queued"}
                        <span class="ml-2 rounded bg-cyan-200 p-1 text-sm">Queued</span>
                    {:else if showItem.status == "creating"}
                        <span class="ml-2 rounded bg-green-200 p-1 text-sm">Creating</span>
                    {:else if showItem.status == "errored"}
                        <span class="ml-2 rounded bg-red-200 p-1 text-sm">Errored</span>
                    {/if}
                </div>
            {/each}
            {#each shows as showItem}
                <div class="flex flex-row justify-between">
                    <a
                        href="/shows/{showItem.id}"
                        class="flex whitespace-nowrap w-full mb-3 align-middle"
                    >
                        <div class="flex-1 mr-4 font-bold">{showItem.title}</div>
                        <div class="text-sm bg-violet-200 rounded-md p-1">
                            {showItem.createdDate.toLocaleDateString()}
                        </div>
                    </a>
                </div>
            {/each}
        </Card>
    </div>
    <div class="m-4">
        <Card title="Create a new Show" classList="mx-auto">
            <p class="text-sm mb-2">
                Create a new show by entering a title and description. You can add episodes to the
                show after it is created. For more control over the show creation process, use the
                <a href="/shows/new">advanced show creation</a> page.
            </p>
            <form on:submit|preventDefault={createShow}>
                <input
                    type="text"
                    bind:value={newShowTitle}
                    placeholder="Show Title"
                    class="border border-gray-300 rounded-md p-2 w-full mb-2"
                />
                <textarea
                    placeholder="Show Description"
                    bind:value={newShowPrompt}
                    class="border border-gray-300 rounded-md p-2 w-full mb-2"
                ></textarea>
                <button class="bg-violet-500 text-white rounded-md p-2 w-full">Create Show</button>
            </form>
        </Card>
    </div>
</div>
