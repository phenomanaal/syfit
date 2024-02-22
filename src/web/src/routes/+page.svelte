<script lang="ts">
	import type { PageServerData } from './$types';

	export let data: PageServerData;
</script>

<h1>
	Welcome {#if data.username}
		{data.username}{/if}!
</h1>

{#if data.detail == 'Could not validate credentials'}
	<a href="/login">Login</a> or <a href="/signup">signup</a>
{:else}
	<form method="POST" action="?/logout"><button formaction="?/logout"> logout </button></form>
{/if}
