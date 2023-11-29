<script>
    import "../app.css";
    import { currentUser } from "$lib/pocketbase";
    import Login from "$lib/components/Login.svelte";
    import LoginCard from "$lib/components/LoginCard.svelte";
    import GuppyPNG from "$lib/assets/guppy.png";
    import SideBar from "$lib/components/SideBar.svelte";

    export const prerender = true;
    // trailing slash:
    export const trailingSlash = "always";
</script>

<div class="flex flex-col h-screen">
    <nav class="block bg-gray-800 text-gray-300 p-4">
        <div class="flex justify-between">
            <div class="flex">
                <a href="/" class="mr-4">
                    <img src={GuppyPNG} width="32" height="32" alt="Study Guppy" /></a
                >
            </div>
            <div class="flex">
                {#if $currentUser == null}
                    <Login />
                {:else}
                    <Login />
                {/if}
            </div>
        </div>
    </nav>
    <div class="h-full">
        {#if $currentUser !== null}
            <div class="flex flex-row w-100 h-full overflow-hidden bg-gray-100">
                <SideBar />
                <div class="bg-gray-100 flex-1">
                    <slot />
                </div>
            </div>
        {:else}
            <LoginCard />
        {/if}
    </div>
</div>
