document.addEventListener("DOMContentLoaded", function () {
    const socket = io();

    // Timer & Calorie Tracker Variables
    let sessionTime = 0;
    let totalCalories = 0;
    let trickQueue = [];
    const maxTricks = 10;
    const tableBody = document.querySelector("#trick-history-table tbody");

    /** 🕒 Update Session Timer Every Second **/
    function updateSessionTime() {
        sessionTime++;
        let hours = Math.floor(sessionTime / 3600);
        let minutes = Math.floor((sessionTime % 3600) / 60);
        let seconds = sessionTime % 60;
        document.getElementById("session-time").innerText = 
            `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
    }

    // Start session timer when page loads
    setInterval(updateSessionTime, 1000);

    /** 🔥 Update Calorie Tracker When New Trick is Detected **/
    function updateCalories() {
        totalCalories += 3; // Assume ~3 kcal burned per trick
        document.getElementById("calories-burned").innerText = `${totalCalories} kcal`;
    }

    /** 🕑 Format the Current Time **/
    function formatTime() {
        let now = new Date();
        let hours = now.getHours() % 12 || 12;
        let minutes = now.getMinutes();
        let ampm = now.getHours() >= 12 ? "PM" : "AM";
        return `${hours}:${minutes < 10 ? "0" : ""}${minutes} ${ampm}`;
    }

    /** 📜 Add Trick to Trick History Table **/
    function addToTable(trickName) {
        let timestamp = formatTime();
        if (trickName == "Waiting for Trick...") {
            return;
        }

        // Prevent adding duplicate tricks in a row
        if (trickQueue.length > 0 && trickQueue[trickQueue.length - 1].trick === trickName) {
            return;
        }

        // Remove the oldest trick if we reach the limit
        if (trickQueue.length >= maxTricks) {
            trickQueue.shift();
            tableBody.deleteRow(0); // Remove first row from table
        }

        // Add new trick to queue
        trickQueue.push({ trick: trickName, time: timestamp });

        // Create a new table row
        let row = document.createElement("tr");
        row.className = "trick-row";
        row.innerHTML = `
            <td>${trickName}</td>
            <td>${timestamp}</td>
        `;

        // Append the row
        tableBody.appendChild(row);

        // Increase calories since a new trick is detected
        updateCalories();
    }

    /** 🎮 Listen for Trick Events from Backend **/
    socket.on("perform_trick", function (data) {
        if (!data || !data.trick_name || !data.gif_url) return;

        // Update Trick Name and GIF on Dashboard
        document.getElementById("trick-name").innerText = `Performing: ${data.trick_name}`;
        document.getElementById("trick-gif").src = data.gif_url;

        // Add trick to table
        addToTable(data.trick_name);
    });
});

