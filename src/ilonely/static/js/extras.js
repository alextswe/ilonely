function getLocation() {
    var message = document.getElementById("location");

    if (!navigator.geolocation) {
        message.innerHTML = "<p>Geolocation is not supported by your browser</p>";
        return;
    }

    function success(position) {
        var lat = position.coords.latitude;
        var long = position.coords.longitude;

        message.innerHTML = "Lat: " + lat + " Long: " + long;
    }

    function error() {
        message.innerHTML = "Unable to retrieve your location";
    }

    message.innerHTML = "<p>Locating…</p>";

    navigator.geolocation.getCurrentPosition(success, error);
}

function sortPeople(radius) {
    profileList = document.getElementById("profiles");
    profileListItems = profileList.getElementsByTagName('li');

    for (i = 0; i < profileListItems.length; i++) {
        dist = document.getElementsByClassName("distances")[i];
        if (parseFloat(dist.innerHTML) < radius) {
            profileListItems[i].style.display = "";
        } else {
            profileListItems[i].style.display = "none";
        }
    }
}