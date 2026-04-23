const API_BASE = process.env.FRESH_API_URL || "https://api.fresh.dev";
export async function requestDeviceCode(clientId) {
    const response = await fetch(`${API_BASE}/device/code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ client_id: clientId }),
    });
    if (!response.ok) {
        throw new Error(`Failed to request device code: ${response.statusText}`);
    }
    return response.json();
}
export async function pollForToken(deviceCode, clientId, initialInterval = 5000) {
    let interval = initialInterval;
    while (true) {
        const response = await fetch(`${API_BASE}/device/token`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                grant_type: "urn:ietf:params:oauth:grant-type:device_code",
                device_code: deviceCode,
                client_id: clientId,
            }),
        });
        const data = await response.json();
        if (data.error) {
            switch (data.error) {
                case "authorization_pending":
                    await sleep(interval);
                    continue;
                case "slow_down":
                    interval += 5000; // Increase by 5 seconds per RFC 8628
                    await sleep(interval);
                    continue;
                case "expired_token":
                    throw new Error("Code expired. Run 'fresh auth login' to try again.");
                case "access_denied":
                    throw new Error("Access denied. Run 'fresh auth login' to try again.");
                default:
                    throw new Error(data.errorDescription || data.error);
            }
        }
        return data;
    }
}
export async function revokeToken(accessToken) {
    try {
        await fetch(`${API_BASE}/device/revoke`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`,
            },
        });
    }
    catch {
        // Ignore revocation errors - we still want to delete local creds
    }
}
export async function getUserInfo(accessToken) {
    try {
        const response = await fetch(`${API_BASE}/me`, {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });
        if (!response.ok)
            return null;
        return response.json();
    }
    catch {
        return null;
    }
}
function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
