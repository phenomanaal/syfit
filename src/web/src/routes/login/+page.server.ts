import type { Actions } from "./$types";
import { env } from '$env/dynamic/private';
import { redirect } from "@sveltejs/kit";

export const actions = {
    login: async ({ request, cookies }) => {
        const data: FormData = await request.formData();

        const response = await fetch(
            "http://127.0.0.1:8000/users/token/",
            {
                method: "POST",
                headers: {
                    "api_key": env.API_KEY
                },
                body: data
            }
        ).then(async (response) => {
            return response
        });
        const response_body = JSON.parse(await response.text())
        if (response.status == 401) {
            return {
                status: response.status,
                body: JSON.stringify({ message: response_body.detail })
            }
        } else if (response.status == 200) { 
            cookies.set('token', response_body.access_token, {
                path: '/',
                httpOnly: true,
                sameSite: 'strict',
                maxAge: 60 * 60
            })
            throw redirect(302, "/")
        }
        return response;

    }
} satisfies Actions;