import { Command } from "commander";
import { requestDeviceCode, pollForToken, type CLIError } from "../../lib/client.js";
import { storeCredential } from "../../lib/storage.js";
import { openBrowser } from "../../utils/open.js";
import { getConfig } from "../../lib/config.js";

function isCLIError(error: unknown): error is CLIError {
  return typeof error === "object" && error !== null && "code" in error && "endpoint" in error;
}

function formatError(error: unknown, apiUrl: string): string {
  if (isCLIError(error)) {
    let msg = `\n❌ Authentication failed`;
    if (error.endpoint) {
      const fullUrl = error.endpoint.startsWith("http")
        ? error.endpoint
        : `${apiUrl}${error.endpoint}`;
      msg += `\n   URL: ${fullUrl}`;
    }
    if (error.statusCode) {
      msg += `\n   Status: ${error.statusCode}`;
    }
    msg += `\n   ${error.message}`;
    if (error.code) {
      msg += `\n   Code: ${error.code}`;
    }
    return msg;
  }
  if (error instanceof Error) {
    return `\n❌ Authentication failed: ${error.message}`;
  }
  return "\n❌ Authentication failed: Unknown error";
}

export const login = new Command()
  .name("login")
  .description("Authenticate with Fresh using device authorization")
  .option("--no-open", "Don't open browser automatically")
  .action(async (options) => {
    const clientId = "fresh-cli";
    const config = getConfig();

    console.log("\n🔐 Fresh CLI Authentication");
    console.log("─".repeat(40));
    console.log(`   API: ${config.apiUrl}`);
    console.log("─".repeat(40) + "\n");

    console.log("Initiating device authentication...\n");

    try {
      // 1. Request device code
      const deviceFlow = await requestDeviceCode(clientId);

      // 2. Display instructions
      const uri = deviceFlow.verificationUriComplete || deviceFlow.verificationUri;
      console.log(`📋 Visit: ${uri}`);
      console.log(`🔑 Code:  ${deviceFlow.userCode}\n`);
      console.log("Waiting for authorization... (press Ctrl+C to cancel)\n");

      // 3. Attempt to open browser
      if (!options.noOpen) {
        const opened = await openBrowser(uri);
        if (!opened) {
          console.log("⚠️  Could not open browser automatically. Please visit the URL above.\n");
        }
      }

      // 4. Poll for token
      const interval = (deviceFlow.interval || 5) * 1000;
      const tokenResponse = await pollForToken(deviceFlow.deviceCode, clientId, interval);

      // 5. Store credential
      const credential = {
        accessToken: tokenResponse.accessToken,
        refreshToken: tokenResponse.refreshToken || "",
        expiresAt: Date.now() + (tokenResponse.expiresIn * 1000),
        scope: tokenResponse.scope || "",
        accountId: tokenResponse.user?.id || "",
        environment: config.environment,
        tokenType: "device_flow",
        issuedAt: Date.now(),
        user: tokenResponse.user,
      };

      await storeCredential(credential);
      console.log("\n✅ Successfully authenticated!");
      if (tokenResponse.user) {
        console.log(`   User: ${tokenResponse.user.name} (${tokenResponse.user.email})\n`);
      } else {
        console.log();
      }
    } catch (error) {
      console.error(formatError(error, config.apiUrl));
      console.log(`\n💡 Tip: Make sure the Fresh server is running and the API endpoint exists.`);
      console.log(`   Current API URL: ${config.apiUrl}`);
      console.log(`   To change it, set FRESH_API_URL environment variable.\n`);
      process.exit(1);
    }
  });
