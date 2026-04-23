import open from "open";
export async function openBrowser(url) {
    try {
        await open(url);
        return true;
    }
    catch {
        return false;
    }
}
