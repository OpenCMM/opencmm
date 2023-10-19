<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
	import { GCodeLoader } from 'three/addons/loaders/GCodeLoader.js';
	import { STLLoader } from 'three/addons/loaders/STLLoader.js';
	import axios from 'axios';
	import { getSphereMesh } from './utils';

	let container: HTMLDivElement;

	onMount(() => {
		// Scene
		const scene = new THREE.Scene();
		scene.background = new THREE.Color(0x3b3939);

		// Camera
		const camera = new THREE.PerspectiveCamera(50, 1000 / 1000, 1, 500);

		camera.position.set(0, -100, 100);

		const loader = new GCodeLoader();
		loader.load('http://127.0.0.1:8000/load/gcode/opencmm', function (obj: any) {
			// rotate the model
			obj.rotateX(Math.PI / 2);
			scene.add(obj);
		});

		const stlLoader = new STLLoader();
		stlLoader.load('http://127.0.0.1:8000/load/model/3dmodel', function (geometry: any) {
			let material = new THREE.MeshPhongMaterial({
				color: 0xf0f0f0
			});
			// Colored binary STL
			if (geometry.hasColors) {
				material = new THREE.MeshPhongMaterial({ opacity: geometry.alpha, vertexColors: true });
			}
			const mesh = new THREE.Mesh(geometry, material);
			scene.add(mesh);
		});

		axios.get(`${BACKEND_URL_LOCAL}/result/edges`).then((res) => {
			if (res.status === 200) {
				const edges = res.data['edges'];

				for (const edge of edges) {
					const [, , x, y, z, rx, ry, rz] = edge;
					const point = new THREE.Vector3(x, y, z);
					const measuredEdge = new THREE.Vector3(rx, ry, rz);
					const pointMesh = getSphereMesh(0.2, 0xfcba03);
					const edgeMesh = getSphereMesh(0.2, 0x00f719);
					pointMesh.position.copy(point);
					edgeMesh.position.copy(measuredEdge);
					scene.add(pointMesh);
					scene.add(edgeMesh);
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
		renderer.setSize(1000, 1000);

		container.appendChild(renderer.domElement);

		// Lights
		scene.add(new THREE.HemisphereLight(0x8d7c7c, 0x494966, 5));

		const controls = new OrbitControls(camera, renderer.domElement);
		controls.mouseButtons = {
			LEFT: THREE.MOUSE.PAN,
			MIDDLE: THREE.MOUSE.DOLLY,
			RIGHT: THREE.MOUSE.ROTATE
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
