import { Command } from "commander";
import { getCredential } from "../../lib/storage.js";
import { getUserInfo } from "../../lib/client.js";

export const whoami = new Command()
  .name("whoami")
  .description("Show current user information")
  .action(async () => {
    const cred = await getCredential();

    if (!cred) {
      console.log("Not authenticated.");
      return;
    }

    // Try to get user info from stored credential first
    if (cred.user) {
      console.log(`User: ${cred.user.name} (${cred.user.email})`);
      console.log(`Account ID: ${cred.user.id}`);
      return;
    }

    // Fallback: try to fetch from API
    const userInfo = await getUserInfo(cred.accessToken);

    if (!userInfo) {
      console.log("Failed to fetch user info. You may need to re-authenticate.");
      return;
    }

    console.log(`User: ${userInfo.name} (${userInfo.email})`);
    console.log(`Account ID: ${userInfo.id}`);
  });
