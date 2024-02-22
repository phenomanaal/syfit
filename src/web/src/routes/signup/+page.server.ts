import type { Actions } from "./$types";
import { env } from '$env/dynamic/private';
import { redirect } from "@sveltejs/kit";

export const actions = {
    signup: async ({ request, cookies }) => {
        console.log("TOP")
        const data: FormData = await request.formData();
        if (!data.has("measurement_system")) { 
            data.append("measurement_system", "imperial")
        }            

        const response = await fetch(
            "http://127.0.0.1:8000/users/signup/",
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
        if (response.status == 409) {
            console.log("here")
            return {
                status: response.status,
                body: JSON.stringify({ message: `Username ${data.get("username")} not available!` })
            }
        } else if (response.status == 200) {
            console.log("or here")
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