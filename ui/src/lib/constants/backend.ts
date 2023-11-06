const BACKEND_PRODUCTION_URL = '192.168.0.19'; 

export const BACKEND_WS_URL =
	process.env.NODE_ENV === 'production' ? `ws://${BACKEND_PRODUCTION_URL}:8000` : 'ws://localhost:8000';
export const BACKEND_URL =
	process.env.NODE_ENV === 'production' ? `http://${BACKEND_PRODUCTION_URL}:8000` : 'http://localhost:8000';
