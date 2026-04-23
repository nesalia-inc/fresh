import { Command } from "commander";
import { fetchUrl, APIError } from "../lib/api.js";

export const fetchCmd = new Command()
  .name("fetch")
  .description("Fetch and extract content from a URL")
  .argument("<url>", "URL to fetch")
  .option("-p, --prompt <text>", "Prompt for content extraction")
  .action(async (url, options) => {
    try {
      console.log(`\nFetching ${url}...\n`);

      const result = await fetchUrl({
        urls: url,
      });

      if (!result.results || result.results.length === 0) {
        console.log("No content found.\n");
        return;
      }

      const firstResult = result.results[0];

      if (firstResult.title) {
        console.log(`Title: ${firstResult.title}`);
      }
      if (firstResult.author) {
        console.log(`Author: ${firstResult.author}`);
      }
      if (firstResult.publishedDate) {
        console.log(`Published: ${firstResult.publishedDate}`);
      }
      console.log("\n" + "-".repeat(50) + "\n");
      if (firstResult.text) {
        console.log(firstResult.text);
      } else if (firstResult.highlights && firstResult.highlights.length > 0) {
        console.log(firstResult.highlights.join("\n\n"));
      }
      console.log("\n" + "-".repeat(50) + "\n");
    } catch (error) {
      if (error instanceof APIError) {
        console.error(`\nFetch failed: ${error.message}`);
        if (error.statusCode === 401) {
          console.error("   Run 'fresh auth login' to authenticate.\n");
        } else {
          console.error();
        }
      } else {
        console.error(`\nFetch failed: ${error instanceof Error ? error.message : "Unknown error"}\n`);
      }
      process.exit(1);
    }
  });