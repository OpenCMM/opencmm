import * as THREE from 'three';

export const getSphereMesh = (radius: number, color: number) => {
	const sphereGeometry = new THREE.SphereGeometry(radius);
	const sphereMaterial = new THREE.MeshBasicMaterial({ color: color });
	const sphereMesh = new THREE.Mesh(sphereGeometry, sphereMaterial);
	return sphereMesh;
};
