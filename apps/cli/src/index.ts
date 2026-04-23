#!/usr/bin/env node

import { Command } from "commander";
import * as authCommands from "./commands/auth/index.js";

const program = new Command();

program
  .name("fresh")
  .description("Fresh CLI - AI-powered web search and fetch")
  .version("0.1.0");

program
  .command("auth")
  .description("Authentication commands")
  .addCommand(authCommands.login)
  .addCommand(authCommands.logout)
  .addCommand(authCommands.status)
  .addCommand(authCommands.whoami);

program.parse();
