import { defineConfig } from 'deesse';
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import { schema } from './db/schema';
import { deviceAuthorization } from 'better-auth/plugins';

export const config = defineConfig({
  name: "DeesseJS App",
  database: drizzle({
    client: new Pool({
      connectionString: process.env.DATABASE_URL,
    }),
    schema,
  }),
  secret: process.env.DEESSE_SECRET!,
  auth: {
    baseURL: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000',
    plugins: [
      deviceAuthorization({
        verificationUri: "/device",
        expiresIn: "30m",
        interval: "5s",
        userCodeLength: 8,
        deviceCodeLength: 40,
      }),
    ],
  },
});