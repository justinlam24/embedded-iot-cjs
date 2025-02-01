const socket = io();

// Animation parameters
let trickQueue = [];
let isAnimating = false;  // Tracks if a trick is currently in progress

socket.on('perform_trick', function (data) {
    document.getElementById('trick-name').innerText = "Performing: " + data.trick_name;
    
    // Add new trick to the queue
    trickQueue.push({
        name: data.trick_name,
        rotation_x: data.rotation_x,
        rotation_y: data.rotation_y,
        rotation_z: data.rotation_z
    });

    // If no animation is in progress, start immediately
    if (!isAnimating) {
        executeNextTrick();
    }
});

// Setup 3D Scene
const container = document.getElementById('skateboard-container');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

// **Corrected Snowboard Model (Box with Rounded Edges)**
const snowboardGeometry = new THREE.BoxGeometry(3, 0.1, 0.7);  // Wide and thin board
const snowboardMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x1e90ff,  // Ice blue color
    metalness: 0.4,   // Slight metallic reflection
    roughness: 0.3    // Smooth and slightly reflective
});
const snowboard = new THREE.Mesh(snowboardGeometry, snowboardMaterial);

// **Ensure Proper Initial Position**
snowboard.rotation.x = Math.PI / 2;  // Lays it flat
snowboard.position.y = 0;  // Keep it at a good height
scene.add(snowboard);

// **Lighting Adjustments**
const light = new THREE.PointLight(0xffffff, 1.2, 100);
light.position.set(5, 5, 5);
scene.add(light);

const ambientLight = new THREE.AmbientLight(0xaaaaaa);
scene.add(ambientLight);

// **Set Camera Position (Move it Back for a Better View)**
camera.position.set(0, 2, 6);
camera.lookAt(snowboard.position);

// **Trick Execution**
function executeNextTrick() {
    if (trickQueue.length === 0) {
        isAnimating = false;
        return;
    }

    isAnimating = true;
    const trick = trickQueue.shift();
    
    const startRotation = { 
        x: snowboard.rotation.x, 
        y: snowboard.rotation.y, 
        z: snowboard.rotation.z 
    };
    const targetRotation = {
        x: startRotation.x + trick.rotation_x,
        y: startRotation.y + trick.rotation_y,
        z: startRotation.z + trick.rotation_z
    };

    animateTrick(startRotation, targetRotation, () => {
        resetBoard(() => {
            executeNextTrick();  // Move on to the next trick after reset
        });
    });
}

// **Smooth Animation Function**
function animateTrick(startRotation, targetRotation, onComplete) {
    let frame = 0;
    const totalFrames = 50;  // Trick duration (2 seconds)

    function step() {
        if (frame < totalFrames) {
            const progress = frame / totalFrames;
            snowboard.rotation.x = startRotation.x + (targetRotation.x - startRotation.x) * progress;
            snowboard.rotation.y = startRotation.y + (targetRotation.y - startRotation.y) * progress;
            snowboard.rotation.z = startRotation.z + (targetRotation.z - startRotation.z) * progress;

            frame++;
            requestAnimationFrame(step);
        } else {
            onComplete();
        }
    }

    step();
}

// **Return to Original Position**
function resetBoard(onComplete) {
    let frame = 0;
    const totalFrames = 50;  // Return duration (2 seconds)
    const startRotation = { 
        x: snowboard.rotation.x, 
        y: snowboard.rotation.y, 
        z: snowboard.rotation.z 
    };
    const targetRotation = { x: 0, y: 0, z: 0 };

    function step() {
        if (frame < totalFrames) {
            const progress = frame / totalFrames;
            snowboard.rotation.x = startRotation.x + (targetRotation.x - startRotation.x) * progress;
            snowboard.rotation.y = startRotation.y + (targetRotation.y - startRotation.y) * progress;
            snowboard.rotation.z = startRotation.z + (targetRotation.z - startRotation.z) * progress;

            frame++;
            requestAnimationFrame(step);
        } else {
            onComplete();
        }
    }

    step();
}

// **Start Animation Loop**
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();
