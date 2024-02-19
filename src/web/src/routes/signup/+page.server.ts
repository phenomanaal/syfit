import type { Actions } from "./$types";
export const actions = {
    signup: async ({ request }) => { 
        const data: FormData = await request.formData();
        fetch(
            "http://127.0.0.1:8000/users/signup/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "api_key": ""
                },
                body: data
            }

        ).then(async (response) => {
            console.log(await response.text())
            return response
        })
    }
}