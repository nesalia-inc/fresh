export function getConfig() {
    return {
        apiUrl: process.env.FRESH_API_URL || "https://fresh.nesalia.com",
        environment: process.env.FRESH_ENV || "production",
    };
}
