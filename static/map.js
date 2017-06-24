var map;

var initMap = function () {
    var midtown = {lat: 40.7561050, lng:-73.9869487};
    map = new google.maps.Map(document.getElementById('map'), {
	zoom: 12,
	center: midtown
    });
}

var add_marker = function(latitude, longitude){
    var marker = new google.maps.Marker({
	posiion: {lat : latitude, lng: longitude},
	map: map
    }); 
}

initMap();
