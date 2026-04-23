import keytar from "keytar";

const SERVICE = "fresh-cli";
const ACCOUNT = "credential";

export interface StoredCredential {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  scope: string;
  accountId: string;
  environment: string;
  tokenType: string;
  issuedAt: number;
}

export async function storeCredential(cred: StoredCredential): Promise<void> {
  await keytar.setPassword(SERVICE, ACCOUNT, JSON.stringify(cred));
}

export async function getCredential(): Promise<StoredCredential | null> {
  const raw = await keytar.getPassword(SERVICE, ACCOUNT);
  return raw ? JSON.parse(raw) : null;
}

export async function deleteCredential(): Promise<void> {
  await keytar.deletePassword(SERVICE, ACCOUNT);
}
