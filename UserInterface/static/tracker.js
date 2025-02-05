document.addEventListener("DOMContentLoaded", function () {
    let startTime = new Date().getTime();
    let caloriesBurned = 0;

    function updateTimer() {
        let elapsedTime = new Date().getTime() - startTime;
        let hours = Math.floor(elapsedTime / 3600000);
        let minutes = Math.floor((elapsedTime % 3600000) / 60000);
        let seconds = Math.floor((elapsedTime % 60000) / 1000);

        document.getElementById("session-timer").innerText =
            (hours < 10 ? "0" : "") + hours + ":" +
            (minutes < 10 ? "0" : "") + minutes + ":" +
            (seconds < 10 ? "0" : "") + seconds;
    }

    function updateCalories() {
        // Burn ~5 calories per minute (~0.08 per second)
        caloriesBurned += 0.08;
        document.getElementById("calories-tracker").innerText =
            caloriesBurned.toFixed(2) + " kcal";
    }

    // Restart timers if they stop
    setInterval(updateTimer, 1000);
    setInterval(updateCalories, 1000);
});
