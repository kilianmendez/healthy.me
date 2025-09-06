"use server"

import { cookies } from "next/headers";


export async function loginAction(formData: FormData) {
    const username = formData.get("username");
    const password = formData.get("password");

    const formBody = new FormData();
    formBody.append("username", username as string);
    formBody.append("password", password as string);

    const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        body: formBody,
        cache: "no-store",
        credentials: "include", // si backend responde con cookies
    });

    if (!response.ok) {
        throw new Error("Login failed");
    }

    const result = await response.json();
    const token = result.access_token;

    const cookieStore = await cookies()

    // Guarda el token en una cookie
    cookieStore.set("access_token", token, {
        httpOnly: true,
        path: "/",
        secure: process.env.NODE_ENV === "production", // solo HTTPS en producción
        maxAge: 60 * 60, // 1 hora
        sameSite: "lax",
    });

    console.log("Token saved in cookie.");
    return result;
}