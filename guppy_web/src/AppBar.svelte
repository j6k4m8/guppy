<script>
    import Login from "./Login.svelte";
    import GuppyPNG from "./assets/guppy.png";
</script>

<div class="appbar">
    <div class="row">
        <div class="column brand">
            <img src={GuppyPNG} width="32" height="32" alt="Study Guppy" />
            Guppy
        </div>
        <div class="column account">
            <Login />
        </div>
    </div>
</div>

<style>
    .appbar {
        background-color: #333;
        color: white;
        padding: 0.5rem;
        margin: 0;
    }

    .brand {
        font-size: 1.5rem;
        padding: 1em;
    }

    .account {
        text-align: right;
    }
</style>
