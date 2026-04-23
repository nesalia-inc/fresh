import { Command } from "commander";
import { getCredential } from "../../lib/storage.js";
export const whoami = new Command()
    .name("whoami")
    .description("Show current user information")
    .action(async () => {
    const cred = await getCredential();
    if (!cred) {
        console.log("Not authenticated.");
        return;
    }
    if (!cred.user) {
        console.log("User info not available. You may need to re-authenticate.");
        return;
    }
    console.log(`User: ${cred.user.name} (${cred.user.email})`);
    console.log(`Account ID: ${cred.user.id}`);
});
