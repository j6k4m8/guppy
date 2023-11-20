<script lang="ts">
    import UserShowList from "./UserShowList.svelte";
    import AppBar from "./AppBar.svelte";
    import { currentUser } from "./lib/pocketbase";
</script>

<main>
    <AppBar />
    {#if $currentUser !== null}
        <UserShowList />
    {:else}
        <h1>Hi!</h1>
    {/if}
</main>
