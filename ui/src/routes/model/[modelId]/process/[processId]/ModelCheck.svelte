<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
	import { STLLoader } from 'three/addons/loaders/STLLoader.js';
	import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
	import axios from 'axios';
	import { getSphereMesh } from '$lib/utils/mesh';

	let container: HTMLDivElement;

	export let modelId: string;
	export let processId: string;
	const canvasWidth = 600;
	const canvasHeight = 600;
	const arcColor = '70a0ff';
	const pairColor = 'cae643';

	onMount(() => {
		// Scene
		const scene = new THREE.Scene();
		scene.background = new THREE.Color(0x3b3939);

		// Camera
		const camera = new THREE.PerspectiveCamera(50, 1000 / 1000, 1, 500);

		camera.position.set(0, 0, 300);

		const stlLoader = new STLLoader();
		stlLoader.load(`${BACKEND_URL}/load/model/${modelId}`, function (geometry: any) {
			let material = new THREE.MeshPhongMaterial({
				color: 0xf0f0f0,
				opacity: 0.6,
				transparent: true
			});
			// Colored binary STL
			if (geometry.hasColors) {
				material = new THREE.MeshPhongMaterial({ opacity: geometry.alpha, vertexColors: true });
			}
			const mesh = new THREE.Mesh(geometry, material);
			scene.add(mesh);
		});

		const labelRenderer = new CSS2DRenderer();
		labelRenderer.setSize(canvasWidth, canvasHeight);
		labelRenderer.domElement.style.position = 'absolute';
		labelRenderer.domElement.style.top = '140px';
		labelRenderer.domElement.style.pointerEvents = 'none';
		container.appendChild(labelRenderer.domElement);

		axios
			.get(`${BACKEND_URL}/result/arcs?model_id=${modelId}&process_id=${processId}`)
			.then((res) => {
				if (res.status === 200) {
					const arcs = res.data['arcs'];

					for (const arc_info of arcs) {
						const [arcId, radius, cx, cy, cz, rradius, rcx, rcy, rcz] = arc_info;
						const center = new THREE.Vector3(cx, cy, cz);
						const measuredCenter = new THREE.Vector3(rcx, rcy, rcz);
						const centerMesh = getSphereMesh(0.3, 0xfcba03);
						const measuredCenterMesh = getSphereMesh(0.3, 0x00f719);
						centerMesh.position.copy(center);
						measuredCenterMesh.position.copy(measuredCenter);
						scene.add(centerMesh);
						scene.add(measuredCenterMesh);

						// Add radius annotation
						// https://sbcode.net/view_source/annotations.html
						// https://sbcode.net/threejs/annotations/
						// https://github.com/Sean-Bradley/Three.js-TypeScript-Boilerplate/tree/annotations

						const arcLabel = document.createElement('div');
						arcLabel.textContent = arcId;
						arcLabel.style.cssText = `color:#${arcColor};font-family:sans-serif;font-size: 17px;`;
						const arcLabelObject = new CSS2DObject(arcLabel);
						arcLabelObject.position.copy(center).add(new THREE.Vector3(-3.0, 3.0, 0));
						scene.add(arcLabelObject);
					}
				}
			});

		axios.get(`${BACKEND_URL}/result/pairs/${modelId}`).then((res) => {
			if (res.status === 200) {
				const pairs = res.data['pairs'];

				for (const pair of pairs) {
					const [pairId, x0, y0, z0, x1, y1, z1] = pair;
					const point0 = new THREE.Vector3(x0, y0, z0);
					const point1 = new THREE.Vector3(x1, y1, z1);
					const lineGeometry = new THREE.BufferGeometry().setFromPoints([point0, point1]);
					const lineMaterial = new THREE.LineBasicMaterial({ color: parseInt(pairColor, 16) });
					const line = new THREE.Line(lineGeometry, lineMaterial);
					scene.add(line);

					const lineLabel = document.createElement('div');
					lineLabel.textContent = pairId;
					lineLabel.style.cssText = `color:#${pairColor};font-family:sans-serif;font-size: 17px;`;
					const lineLabelObject = new CSS2DObject(lineLabel);
					const midpoint = new THREE.Vector3().lerpVectors(point0, point1, 0.5);
					lineLabelObject.position.copy(midpoint).add(new THREE.Vector3(-3.0, 3.0, 0));
					scene.add(lineLabelObject);
				}
			}
		});

		// Grid on xy plane
		const size = 500;
		const divisions = 50;
		const gridHelper = new THREE.GridHelper(size, divisions, 0xb3b3b3, 0x555555);
		gridHelper.geometry.rotateX(Math.PI / 2);
		scene.add(gridHelper);

		// Renderer
		const renderer = new THREE.WebGLRenderer({ antialias: true });
		renderer.setSize(canvasWidth, canvasHeight);

		container.appendChild(renderer.domElement);

		// Lights
		scene.add(new THREE.HemisphereLight(0x8d7c7c, 0x494966, 5));

		const controls = new OrbitControls(camera, renderer.domElement);
		controls.mouseButtons = {
			LEFT: THREE.MOUSE.ROTATE,
			MIDDLE: THREE.MOUSE.DOLLY,
			RIGHT: THREE.MOUSE.PAN
		};
		controls.target.set(0, 0, 2);
		controls.update();

		animate();

		function animate() {
			requestAnimationFrame(animate);
			renderer.render(scene, camera);
			labelRenderer.render(scene, camera);
		}

		// Clean up the Three.js scene on component unmount
		return () => {
			renderer.dispose();
			scene.remove(gridHelper);
		};
	});
</script>

<div bind:this={container} />
