#!/usr/bin/env node

import { Command } from "commander";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import * as authCommands from "./commands/auth/index.js";
import { searchCmd } from "./commands/search.js";
import { fetchCmd } from "./commands/fetch.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const packageJson = JSON.parse(readFileSync(join(__dirname, "..", "package.json"), "utf8"));

const program = new Command();

program
  .name("fresh")
  .description("Fresh CLI - AI-powered web search and fetch")
  .version(packageJson.version);

program
  .command("auth")
  .description("Authentication commands")
  .addCommand(authCommands.login)
  .addCommand(authCommands.logout)
  .addCommand(authCommands.status)
  .addCommand(authCommands.whoami);

program.addCommand(searchCmd);
program.addCommand(fetchCmd);

program.parse();
