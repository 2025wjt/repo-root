import type { ApiFailure, ApiResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

export class ApiError extends Error {
  errorCode: string;
  details?: Record<string, unknown>;
  status?: number;

  constructor(message: string, errorCode: string, details?: Record<string, unknown>, status?: number) {
    super(message);
    this.name = "ApiError";
    this.errorCode = errorCode;
    this.details = details;
    this.status = status;
  }
}

type RequestMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface RequestOptions extends Omit<RequestInit, "body" | "method"> {
  method?: RequestMethod;
  body?: unknown;
  query?: Record<string, string | number | boolean | null | undefined>;
}

function toQueryString(query?: RequestOptions["query"]) {
  if (!query) {
    return "";
  }

  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value === null || value === undefined || value === "") {
      return;
    }
    params.set(key, String(value));
  });

  const serialized = params.toString();
  return serialized ? `?${serialized}` : "";
}

function normalizeUrl(path: string, query?: RequestOptions["query"]) {
  const prefix = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${prefix}${toQueryString(query)}`;
}

async function parseResponse<T>(response: Response): Promise<ApiResponse<T>> {
  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json")
    ? ((await response.json()) as ApiResponse<T>)
    : undefined;

  if (!response.ok) {
    const fallbackError: ApiFailure = {
      success: false,
      error_code: `HTTP_${response.status}`,
      message: response.statusText || "请求失败",
    };
    const errorPayload = payload && !payload.success ? payload : fallbackError;
    throw new ApiError(errorPayload.message, errorPayload.error_code, errorPayload.details, response.status);
  }

  if (!payload) {
    throw new ApiError("接口返回内容不是 JSON", "INVALID_RESPONSE");
  }

  return payload;
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<ApiResponse<T>> {
  const headers: HeadersInit = {
    Accept: "application/json",
    ...(options.headers ?? {}),
  };

  if (options.body !== undefined) {
    (headers as Record<string, string>)["Content-Type"] = "application/json";
  }

  const response = await fetch(normalizeUrl(path, options.query), {
    method: options.method ?? "GET",
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
    credentials: options.credentials ?? "same-origin",
    signal: options.signal,
  });

  return parseResponse<T>(response);
}

export async function requestData<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const result = await request<T>(path, options);
  if (!result.success) {
    throw new ApiError(result.message, result.error_code, result.details);
  }
  return result.data;
}
