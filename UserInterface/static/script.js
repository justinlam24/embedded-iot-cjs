const socket = io();

socket.on('perform_trick', function (data) {
    if (!data || !data.gif_url) return;  // Ignore invalid tricks

    console.log(`Received Trick: ${data.trick_name} -> ${data.gif_url}`);

    // Update trick name
    document.getElementById('trick-name').innerText = `Performing: ${data.trick_name}`;

    // Update and show GIF
    const gifElement = document.getElementById('trick-gif');
    gifElement.src = data.gif_url;
    gifElement.style.display = "block";

    // Restart GIF animation
    gifElement.onload = function () {
        gifElement.style.display = "none";
        void gifElement.offsetWidth;  // Force reflow
        gifElement.style.display = "block";
    };
});

