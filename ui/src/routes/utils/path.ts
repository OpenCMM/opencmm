import { goto } from '$app/navigation';

export function goToFilePage(model_id: number, status: number) {
	switch (status) {
		case 0:
			goto(`/file/setup?id=${model_id}`);
			break;
		case 1:
			goto(`/file/start?id=${model_id}`);
			break;
		default:
			goto(`/model?id=${model_id}`);
			break;
	}
}
