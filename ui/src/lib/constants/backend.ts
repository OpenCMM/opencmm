export const BACKEND_WS_URL =
	process.env.NODE_ENV === 'production' ? 'ws://localhost:8000' : 'ws://backend:8000';
export const BACKEND_URL =
	process.env.NODE_ENV === 'production' ? 'http://localhost:8000' : 'http://backend:8000';
