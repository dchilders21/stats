function changeTeam() {
    location.href = "/" + teams.value;
}

window.onload = function() {
    var teams = document.getElementById("teams");
    teams.addEventListener("change", changeTeam, false);
}