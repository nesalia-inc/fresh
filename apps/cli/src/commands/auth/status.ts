import { Command } from "commander";
import { getCredential } from "../../lib/storage.js";

export const status = new Command()
  .name("status")
  .description("Check authentication status")
  .action(async () => {
    const cred = await getCredential();

    if (!cred) {
      console.log("Not authenticated. Run 'fresh auth login' to login.");
      return;
    }

    const now = Date.now();
    if (cred.expiresAt < now) {
      console.log("Token expired. Run 'fresh auth login' to re-authenticate.");
      return;
    }

    console.log(`Authenticated`);
    console.log(`Expires: ${new Date(cred.expiresAt).toLocaleString()}`);
    console.log(`Environment: ${cred.environment}`);
  });
