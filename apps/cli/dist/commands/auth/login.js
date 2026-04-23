import { Command } from "commander";
import { requestDeviceCode, pollForToken } from "../../lib/client.js";
import { storeCredential } from "../../lib/storage.js";
import { openBrowser } from "../../utils/open.js";
export const login = new Command()
    .name("login")
    .description("Authenticate with Fresh using device authorization")
    .option("--no-open", "Don't open browser automatically")
    .action(async (options) => {
    const clientId = "fresh-cli";
    console.log("\nInitiating device authentication...\n");
    try {
        // 1. Request device code
        const deviceFlow = await requestDeviceCode(clientId);
        // 2. Display instructions
        const uri = deviceFlow.verificationUriComplete || deviceFlow.verificationUri;
        console.log(`Visit: ${uri}`);
        console.log(`Code:  ${deviceFlow.userCode}\n`);
        // 3. Attempt to open browser
        if (!options.noOpen) {
            const opened = await openBrowser(uri);
            if (!opened) {
                console.log("(Could not open browser automatically)\n");
            }
        }
        // 4. Poll for token
        console.log("Waiting for authorization...");
        const interval = (deviceFlow.interval || 5) * 1000;
        const tokenResponse = await pollForToken(deviceFlow.deviceCode, clientId, interval);
        // 5. Store credential
        const credential = {
            accessToken: tokenResponse.accessToken,
            refreshToken: tokenResponse.refreshToken || "",
            expiresAt: Date.now() + (tokenResponse.expiresIn * 1000),
            scope: tokenResponse.scope || "",
            accountId: "",
            environment: "production",
            tokenType: "device_flow",
            issuedAt: Date.now(),
        };
        await storeCredential(credential);
        console.log("\nSuccessfully authenticated!\n");
    }
    catch (error) {
        console.error(`\nAuthentication failed: ${error instanceof Error ? error.message : "Unknown error"}\n`);
        process.exit(1);
    }
});
