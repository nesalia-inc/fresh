export interface CLIConfig {
  apiUrl: string;
  environment: string;
}

export function getConfig(): CLIConfig {
  return {
    apiUrl: process.env.FRESH_API_URL || "https://fresh.nesalia.com",
    environment: process.env.FRESH_ENV || "production",
  };
}
