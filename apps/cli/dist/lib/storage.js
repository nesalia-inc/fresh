import keytar from "keytar";
const SERVICE = "fresh-cli";
const ACCOUNT = "credential";
export async function storeCredential(cred) {
    await keytar.setPassword(SERVICE, ACCOUNT, JSON.stringify(cred));
}
export async function getCredential() {
    const raw = await keytar.getPassword(SERVICE, ACCOUNT);
    return raw ? JSON.parse(raw) : null;
}
export async function deleteCredential() {
    await keytar.deletePassword(SERVICE, ACCOUNT);
}
