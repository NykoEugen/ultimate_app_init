const baseUrl = import.meta.env.VITE_API_URL || '';

const jsonHeaders = {
  'Content-Type': 'application/json',
};

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
    headers: jsonHeaders,
  });

  return handleResponse(response);
}

export async function apiPost(path, body) {
  const response = await fetch(resolveUrl(path), {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(body ?? {}),
  });

  return handleResponse(response);
}

export async function apiPut(path, body) {
  const response = await fetch(resolveUrl(path), {
    method: 'PUT',
    headers: jsonHeaders,
    body: JSON.stringify(body ?? {}),
  });

  return handleResponse(response);
}
