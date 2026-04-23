import { Command } from "commander";
import { getCredential, deleteCredential } from "../../lib/storage.js";
import { revokeToken } from "../../lib/client.js";

export const logout = new Command()
  .name("logout")
  .description("Sign out and clear stored credentials")
  .action(async () => {
    const cred = await getCredential();

    if (!cred) {
      console.log("Not logged in.\n");
      return;
    }

    // Attempt server-side revocation
    await revokeToken(cred.accessToken);

    // Delete local credentials
    await deleteCredential();

    console.log("Successfully logged out.\n");
  });
