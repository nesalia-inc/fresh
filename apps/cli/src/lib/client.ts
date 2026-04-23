const API_BASE = process.env.FRESH_API_URL || "https://fresh.nesalia.com/api/auth";

export interface CLIError extends Error {
  code?: string;
  statusCode?: number;
  endpoint?: string;
}

function createCLIError(message: string, options: { code?: string; statusCode?: number; endpoint?: string } = {}): CLIError {
  const error = new Error(message) as CLIError;
  error.code = options.code;
  error.statusCode = options.statusCode;
  error.endpoint = options.endpoint;
  return error;
}

export interface DeviceCodeResponse {
  deviceCode: string;
  userCode: string;
  verificationUri: string;
  verificationUriComplete?: string;
  expiresIn: number;
  interval: number;
}

function toDeviceCodeResponse(data: any): DeviceCodeResponse {
  return {
    deviceCode: data.device_code,
    userCode: data.user_code,
    verificationUri: data.verification_uri,
    verificationUriComplete: data.verification_uri_complete,
    expiresIn: data.expires_in,
    interval: data.interval,
  };
}

export interface TokenResponse {
  accessToken: string;
  refreshToken?: string;
  expiresIn: number;
  scope?: string;
  error?: string;
  errorDescription?: string;
}

function toTokenResponse(data: any): TokenResponse {
  return {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    expiresIn: data.expires_in,
    scope: data.scope,
    error: data.error,
    errorDescription: data.error_description,
  };
}

export async function requestDeviceCode(clientId: string): Promise<DeviceCodeResponse> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE}/device/code`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ client_id: clientId }),
    });
  } catch (err) {
    const error = err as Error;
    if (error.message.includes("fetch failed") || error.message.includes("ECONNREFUSED") || error.message.includes("ENOTFOUND")) {
      throw createCLIError(
        `Cannot connect to ${API_BASE}. Is the Fresh server running?\n` +
        `Hint: Set FRESH_API_URL environment variable to your server URL.\n` +
        `Example: FRESH_API_URL=http://localhost:3000 fresh auth login`,
        { code: "NETWORK_ERROR", endpoint: "/device/code" }
      );
    }
    throw createCLIError(`Network error: ${error.message}`, { code: "NETWORK_ERROR", endpoint: "/device/code" });
  }

  if (!response.ok) {
    let errorBody: { error?: string; error_description?: string } = {};
    try {
      errorBody = await response.json();
    } catch {
      // ignore parse error
    }
    throw createCLIError(
      errorBody.error_description || errorBody.error || `HTTP ${response.status}: ${response.statusText}`,
      { code: errorBody.error || "REQUEST_FAILED", statusCode: response.status, endpoint: "/device/code" }
    );
  }

  return toDeviceCodeResponse(await response.json());
}

export async function pollForToken(
  deviceCode: string,
  clientId: string,
  initialInterval: number = 5000
): Promise<TokenResponse> {
  let interval = initialInterval;
  let lastError: CLIError | null = null;

  while (true) {
    let response: Response;

    try {
      response = await fetch(`${API_BASE}/device/token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          grant_type: "urn:ietf:params:oauth:grant-type:device_code",
          device_code: deviceCode,
          client_id: clientId,
        }),
      });
    } catch (err) {
      const error = err as Error;
      if (error.message.includes("fetch failed") || error.message.includes("ECONNREFUSED") || error.message.includes("ENOTFOUND")) {
        throw createCLIError(
          `Cannot connect to ${API_BASE}. Is the Fresh server running?\n` +
          `Hint: Set FRESH_API_URL environment variable to your server URL.`,
          { code: "NETWORK_ERROR", endpoint: "/device/token" }
        );
      }
      throw createCLIError(`Network error: ${error.message}`, { code: "NETWORK_ERROR", endpoint: "/device/token" });
    }

    const data = toTokenResponse(await response.json());

    if (data.error) {
      switch (data.error) {
        case "authorization_pending":
          lastError = null;
          await sleep(interval);
          continue;
        case "slow_down":
          lastError = null;
          interval += 5000; // Increase by 5 seconds per RFC 8628
          await sleep(interval);
          continue;
        case "expired_token":
          throw createCLIError(
            "Code expired. Run 'fresh auth login' to try again.",
            { code: "EXPIRED_TOKEN", endpoint: "/device/token" }
          );
        case "access_denied":
          throw createCLIError(
            "Access denied by user. Run 'fresh auth login' to try again.",
            { code: "ACCESS_DENIED", endpoint: "/device/token" }
          );
        case "authorization_declined":
          throw createCLIError(
            "Authorization was declined. Run 'fresh auth login' to try again.",
            { code: "AUTHORIZATION_DECLINED", endpoint: "/device/token" }
          );
        default:
          throw createCLIError(
            data.errorDescription || `OAuth error: ${data.error}`,
            { code: data.error, statusCode: response.status, endpoint: "/device/token" }
          );
      }
    }

    return data;
  }
}

export async function revokeToken(accessToken: string): Promise<void> {
  try {
    await fetch(`${API_BASE}/device/revoke`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
    });
  } catch {
    // Ignore revocation errors - we still want to delete local creds
  }
}

export async function getUserInfo(accessToken: string): Promise<{
  id: string;
  name: string;
  email: string;
} | null> {
  try {
    const response = await fetch(`${API_BASE}/get-session`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) return null;
    const data = await response.json();
    if (data?.user) {
      return {
        id: data.user.id,
        name: data.user.name,
        email: data.user.email,
      };
    }
    return null;
  } catch {
    return null;
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
