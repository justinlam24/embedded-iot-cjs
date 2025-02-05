document.addEventListener("DOMContentLoaded", function () {
    // Mock trick history (random timestamps)
    const tricks = [
        { name: "Kickflip", timestamp: "12:30 PM" },
        { name: "Heelflip", timestamp: "12:35 PM" },
        { name: "Shuv it", timestamp: "12:40 PM" },
        { name: "Front shuv", timestamp: "12:45 PM" },
        { name: "360 shuv it", timestamp: "12:50 PM" },
        { name: "360 shuv", timestamp: "12:55 PM" },
        { name: "Ollie", timestamp: "1:00 PM" }
    ];

    const timeline = document.getElementById("trick-timeline");

    tricks.forEach(trick => {
        const item = document.createElement("div");
        item.classList.add("timeline-item");

        item.innerHTML = `
            <div class="timestamp">${trick.timestamp}</div>
            <div class="trick-name">${trick.name}</div>
        `;

        timeline.appendChild(item);
    });
});
