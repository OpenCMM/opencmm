<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
	import { GCodeLoader } from 'three/addons/loaders/GCodeLoader.js';
	import { STLLoader } from 'three/addons/loaders/STLLoader.js';
	import axios from 'axios';
	import { getSphereMesh } from '$lib/utils/mesh';

	let container: HTMLDivElement;
	export let modelId: string;
	export let processId: string;
	export let offset: number[];

	onMount(() => {
		// Scene
		const scene = new THREE.Scene();
		scene.background = new THREE.Color(0x3b3939);

		// Camera
		const camera = new THREE.PerspectiveCamera(50, 1000 / 1000, 1, 500);

		camera.position.set(0, 0, 300);

		const loader = new GCodeLoader();
		loader.load(`${BACKEND_URL}/load/gcode/${modelId}`, function (obj: any) {
			// rotate the model
			obj.rotateX(Math.PI / 2);
			scene.add(obj);
		});

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
			mesh.geometry.translate(offset[0], offset[1], offset[2]); // apply translation
			scene.add(mesh);
		});

		axios.get(`${BACKEND_URL}/result/debug/mtconnect/points/${processId}`).then((res) => {
			if (res.status === 200) {
				const points = res.data['points'];
				for (const _point of points) {
					const [_id, x, y, _z, _distance] = _point;
					const point = new THREE.Vector3(x, y, 0.0);
					const pointMesh = getSphereMesh(0.3, 0xfcba03);
					pointMesh.position.copy(point);
					scene.add(pointMesh);
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
		renderer.setSize(800, 800);

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
		}

		// Clean up the Three.js scene on component unmount
		return () => {
			renderer.dispose();
			scene.remove(gridHelper);
		};
	});
</script>

<div bind:this={container} />
