import { goto } from '$app/navigation';

export function redirectToFilePage(model_id: number, status: number) {
	switch (status) {
		case 0:
			goto(`/file/setup?id=${model_id}`);
			break;
		case 1:
			goto(`/file/start?id=${model_id}`);
			break;
		default:
			break;
	}
}
