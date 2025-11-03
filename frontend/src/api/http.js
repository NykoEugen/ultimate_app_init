const baseUrl = import.meta.env.VITE_API_URL || '';

const jsonHeaders = {
  'Content-Type': 'application/json',
};

let authToken = null;

export function setAuthToken(token) {
  authToken = token ? String(token) : null;
}

export function getAuthToken() {
  return authToken;
}

function buildHeaders() {
  const headers = { ...jsonHeaders };
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }
  return headers;
}

async function handleResponse(response) {
  if (!response.ok) {
    const error = new Error(`Request failed with status ${response.status}`);
    error.status = response.status;
    error.details = await response.text();
    throw error;
  }

  const contentType = response.headers.get('content-type') || '';
  return contentType.includes('application/json')
    ? response.json()
    : response.text();
}

const resolveUrl = (path) => {
  if (!path) {
    throw new Error('Path is required for API requests.');
  }

  if (!baseUrl) {
    throw new Error('VITE_API_URL is not defined. Set it in your environment configuration.');
  }

  return new URL(path, baseUrl).toString();
};

export async function apiGet(path) {
  const response = await fetch(resolveUrl(path), {
    method: 'GET',
    headers: buildHeaders(),
  });

  return handleResponse(response);
}

export async function apiPost(path, body) {
  const response = await fetch(resolveUrl(path), {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify(body ?? {}),
  });

  return handleResponse(response);
}

export async function apiPut(path, body) {
  const response = await fetch(resolveUrl(path), {
    method: 'PUT',
    headers: buildHeaders(),
    body: JSON.stringify(body ?? {}),
  });

  return handleResponse(response);
}
