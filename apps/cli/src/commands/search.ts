import { Command } from "commander";
import { search, APIError } from "../lib/api.js";

export const searchCmd = new Command()
  .name("search")
  .description("Search the web using Exa.ai")
  .option("-q, --query <text>", "Search query")
  .option("-l, --limit <number>", "Maximum number of results", "10")
  .option("-t, --type <type>", "Type of search (auto, fast, deep-lite, deep, deep-reasoning, instant)", "auto")
  .action(async (options) => {
    if (!options.query) {
      console.error("\nError: --query is required\n");
      console.error("Usage: fresh search --query <text> [--limit <number>] [--type <type>]\n");
      process.exit(1);
    }

    try {
      console.log("\nSearching...\n");

      const result = await search({
        query: options.query,
        numResults: parseInt(options.limit, 10),
        type: options.type as "auto" | "fast" | "deep-lite" | "deep" | "deep-reasoning" | "instant",
      });

      if (!result.results || result.results.length === 0) {
        console.log("No results found.\n");
        return;
      }

      console.log(`Found ${result.results.length} results:\n`);

      result.results.forEach((r, i) => {
        console.log(`${i + 1}. ${r.title}`);
        console.log(`   URL: ${r.url}`);
        if (r.score !== undefined) {
          console.log(`   Score: ${(r.score * 100).toFixed(1)}%`);
        }
        if (r.highlights && r.highlights.length > 0) {
          const snippet = r.highlights[0];
          console.log(`   ${snippet.substring(0, 200)}${snippet.length > 200 ? "..." : ""}`);
        } else if (r.text) {
          console.log(`   ${r.text.substring(0, 200)}${r.text.length > 200 ? "..." : ""}`);
        }
        console.log();
      });
    } catch (error) {
      if (error instanceof APIError) {
        console.error(`\nSearch failed: ${error.message}`);
        if (error.statusCode === 401) {
          console.error("   Run 'fresh auth login' to authenticate.\n");
        } else {
          console.error();
        }
      } else {
        console.error(`\nSearch failed: ${error instanceof Error ? error.message : "Unknown error"}\n`);
      }
      process.exit(1);
    }
  });