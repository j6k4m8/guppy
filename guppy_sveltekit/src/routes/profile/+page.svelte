<script lang="ts">
    import Card from "$lib/components/Card.svelte";
    import { currentUser, pb } from "$lib/pocketbase";

    function signOut() {
        pb.authStore.clear();
    }
</script>

<div>
    <div class="flex justify-around mt-12 max-w-xl mx-auto">
        <Card classList="w-full">
            <div slot="title">
                <div class="flex bg-gray-100 rounded-t-lg p-3">
                    <h1 class="text-2xl font-bold">Profile</h1>
                    <div class="flex-grow"></div>
                    <button
                        class="bg-red-400 hover:bg-red-100 text-white py-1 px-2 rounded"
                        on:click={signOut}
                    >
                        Sign Out
                    </button>
                </div>
            </div>
            <div slot="body">
                <img
                    src={$currentUser?.avatar || "https://i.pravatar.cc/150?u=1"}
                    class="rounded-full w-32 h-32 mx-auto mb-4"
                    alt="Profile picture for {$currentUser?.name}"
                />
                <h2 class="text-xl font-bold mb-2 text-center">
                    {$currentUser?.name}
                </h2>
                <!-- Table of vitals -->
                <table class="text-left mb-4 w-full">
                    <tbody class="text-sm">
                        <tr class="border-b">
                            <td class="font-bold">Username</td>
                            <td class="text-right">
                                <pre>@{$currentUser?.username}</pre>
                            </td>
                        </tr>
                        <tr class="border-b">
                            <td class="font-bold">User since</td>
                            <td class="text-right">{$currentUser?.created}</td>
                        </tr>
                        <tr class="">
                            <td class="font-bold">Email</td>
                            <td class="text-right">{$currentUser?.email.slice(0, 8)}...</td>
                        </tr>
                    </tbody>
                </table>
                <!-- {JSON.stringify($currentUser, null, 2)} -->
            </div>
        </Card>
    </div>
</div>
