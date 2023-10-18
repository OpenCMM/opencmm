<script lang="ts">
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
	import { STLLoader } from 'three/addons/loaders/STLLoader.js';

	let container: HTMLDivElement;

	onMount(() => {
		// Scene
		const scene = new THREE.Scene();
		scene.background = new THREE.Color(0x999999);

		// Camera
		const camera = new THREE.PerspectiveCamera(50, 1000 / 1000, 1, 500);

		camera.position.set(20, 20, 20);

		const loader = new STLLoader();
		loader.load('http://127.0.0.1:8000/load/model/3dmodel', function (geometry: any) {
			let material = new THREE.MeshPhongMaterial({
				color: 0xff9c7c,
				specular: 0x494949,
				shininess: 200
			});
			// Colored binary STL
			if (geometry.hasColors) {
				material = new THREE.MeshPhongMaterial({ opacity: geometry.alpha, vertexColors: true });
			}
			const mesh = new THREE.Mesh(geometry, material);
			const scaleFactor = 0.1; // Adjust this value as needed
			mesh.scale.set(scaleFactor, scaleFactor, scaleFactor);
			mesh.castShadow = true;
			mesh.receiveShadow = true;

			scene.add(mesh);
		});

		// Grid
		const size = 50;
		const divisions = 50;
		const gridHelper = new THREE.GridHelper(size, divisions, 0xffffff, 0x555555);
		gridHelper.position.y = -0.5;

		scene.add(gridHelper);
		gridHelper.receiveShadow = true;

		// Renderer
		const renderer = new THREE.WebGLRenderer({ antialias: true });
		renderer.setSize(1000, 1000);
		renderer.useLegacyLights = false;

		container.appendChild(renderer.domElement);

		// Lights
		scene.add(new THREE.HemisphereLight(0x8d7c7c, 0x494966, 3));

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
