<script lang="ts">
    import { pb, currentUser } from "./lib/pocketbase";

    let title: string = "";
    let prompt: string = "";

    async function createShow() {
        try {
            await pb.collection("show_requests").create({ title, prompt, creator: $currentUser.id, status: "queued" });
        } catch (e) {
            console.error(e);
        }
        title = "";
    }
</script>

<h2>new show</h2>

<form on:submit|preventDefault={createShow}>
    <label>
        Title:
        <input type="text" bind:value={title} />
    </label>

    <label>
        Prompt:
        <textarea bind:value={prompt} />
    </label>

    <button type="submit">Create</button>
</form>

<style>
    form {
        display: flex;
        flex-direction: column;
    }

    label {
        display: flex;
        flex-direction: column;
        margin-bottom: 1rem;
    }

    input,
    textarea {
        padding: 0.5rem;
        font-size: 1rem;
        border: 1px solid #ccc;
        border-radius: 0.25rem;
    }

    button {
        padding: 0.5rem;
        font-size: 1rem;
        border: 1px solid #ccc;
        border-radius: 0.25rem;
    }
</style>
