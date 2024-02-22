
import type { PageServerLoad } from './$types';
import type { Actions } from "./$types";
import { env } from '$env/dynamic/private';
import { redirect } from "@sveltejs/kit";


export const load: PageServerLoad = async ({ cookies }) => {
    const token = cookies.get('token');
    const response = await fetch(
        "http://127.0.0.1:8000/users/me/",
        {
            method: "GET",
            headers: {
                "api_key": env.API_KEY,
                "Authorization": `Bearer ${token}`
            }
        }
    ).then(async (response) => {
        return await response.json()
    });
    return response;
};

export const actions = {
    signout: async ({ request, cookies }) => {
        cookies.delete("token", {path: "/"})
        throw redirect(302, "/")
    }
} satisfies Actions