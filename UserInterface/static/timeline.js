document.addEventListener("DOMContentLoaded", function () {
    let trickQueue = [];
    const maxTricks = 10;
    const tableBody = document.querySelector("#trick-history-table tbody");

    function formatTime() {
        let now = new Date();
        let hours = now.getHours() % 12 || 12;
        let minutes = now.getMinutes();
        let ampm = now.getHours() >= 12 ? "PM" : "AM";
        return `${hours}:${minutes < 10 ? "0" : ""}${minutes} ${ampm}`;
    }

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
    }

    // Expose function globally for tracker.js
    window.addToTable = addToTable;
});
