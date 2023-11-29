import { pb } from '$lib/pocketbase.js'


export const load = async ({ params }) => {
    const show = await pb.collection('shows').getOne(params.showId);
    const episodes = await pb.collection('episodes').getFullList({
        show: params.showId,
        sort: 'show_index',
    });
    return {
        showId: params.showId,
        show,
        episodes
    }
}