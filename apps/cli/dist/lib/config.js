export function getConfig() {
    return {
        apiUrl: process.env.FRESH_API_URL || "https://api.fresh.dev",
        environment: process.env.FRESH_ENV || "production",
    };
}
