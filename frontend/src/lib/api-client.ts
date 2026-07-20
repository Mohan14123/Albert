import { getAccessToken, clearTokens, setTokens, getRefreshToken } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

interface FetchOptions extends RequestInit {
  skipAuth?: boolean;
}

class ApiClientError extends Error {
  status: number;
  data: unknown;
  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.data = data;
  }
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch {
    return null;
  }
}

export async function apiClient<T = unknown>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { skipAuth = false, headers: customHeaders, ...rest } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(customHeaders as Record<string, string>),
  };

  if (!skipAuth) {
    const token = getAccessToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  let res = await fetch(`${API_BASE}${endpoint}`, { headers, ...rest });

  // If 401, try refreshing the token once
  if (res.status === 401 && !skipAuth) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers["Authorization"] = `Bearer ${newToken}`;
      res = await fetch(`${API_BASE}${endpoint}`, { headers, ...rest });
    } else {
      clearTokens();
      if (typeof window !== "undefined") {
        window.location.href = "/";
      }
      throw new ApiClientError("Session expired", 401);
    }
  }

  if (res.status === 204) {
    return undefined as T;
  }

  const data = await res.json();

  if (!res.ok) {
    throw new ApiClientError(
      data?.detail?.message || data?.detail || "Request failed",
      res.status,
      data
    );
  }

  return data as T;
}

/**
 * Create an SSE (Server-Sent Events) connection and yield parsed events.
 */
export function createSSEStream(
  endpoint: string,
  onEvent: (event: { type: string; data: unknown }) => void,
  onError?: (error: Error) => void,
  onDone?: () => void
): () => void {
  const token = getAccessToken();
  const url = `${API_BASE}${endpoint}`;

  const eventSource = new EventSource(
    token ? `${url}${url.includes("?") ? "&" : "?"}token=${token}` : url
  );

  eventSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      onEvent({ type: "message", data });
      if (data.done) {
        eventSource.close();
        onDone?.();
      }
    } catch {
      onEvent({ type: "message", data: e.data });
    }
  };

  eventSource.addEventListener("connected", (e) => {
    const messageEvent = e as MessageEvent;
    try {
      onEvent({ type: "connected", data: JSON.parse(messageEvent.data) });
    } catch {
      onEvent({ type: "connected", data: messageEvent.data });
    }
  });

  eventSource.addEventListener("heartbeat", () => {
    // Keep alive — no-op
  });

  eventSource.addEventListener("error", (e) => {
    const messageEvent = e as MessageEvent;
    try {
      const data = JSON.parse(messageEvent.data);
      onError?.(new Error(data.error || "SSE error"));
    } catch {
      onError?.(new Error("SSE connection error"));
    }
    eventSource.close();
  });

  eventSource.onerror = () => {
    eventSource.close();
    onDone?.();
  };

  // Return cleanup function
  return () => {
    eventSource.close();
  };
}

export { ApiClientError };
