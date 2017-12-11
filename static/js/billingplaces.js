// This example displays an address form, using the autocomplete feature
// of the Google Places API to help users fill in the information.

// This example requires the Places library. Include the libraries=places
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">

var placeSearch, autocomplete2;
var componentForm2 = {
    street_number: 'short_name',
    // route: 'long_name',
    locality: 'long_name',
    administrative_area_level_1: 'short_name',
    country: 'short_name',
    postal_code: 'short_name'
};

var fieldNames2 = {
    street_number: "street",
    locality: "city",
    administrative_area_level_1: "state",
    postal_code: "zip_code",
    country: "country"
}

var element2 = document.getElementById("autocomplete");

var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;

var observer2 = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
        if (mutation.type == "attributes") {
            element.removeAttribute('placeholder');
        }
    });
});

observer2.observe(element, {
    attributes: true
});

function initAutocomplete() {
    // Create the autocomplete object, restricting the search to geographical
    // location types.
    autocomplete2 = new google.maps.places.Autocomplete(
            /** @type {!HTMLInputElement} */(document.getElementById('autocomplete')),
        { types: ['geocode'] });

    // When the user selects an address from the dropdown, populate the address
    // fields in the form.
    autocomplete2.addListener('place_changed', fillInAddress2);
}

function fillInAddress2() {
    // Get the place details from the autocomplete object.
    document.getElementById("billing-autocomplete").id = "street_number"
    var place = autocomplete2.getPlace();
    for (var component in componentForm2) {
        document.getElementById(component).value = '';
        document.getElementById(component).disabled = false;
    }

    // Get each component of the address from the place details
    // and fill the corresponding field on the form.
    for (var i = 0; i < place.address_components.length; i++) {
        var addressType = place.address_components[i].types[0];
        if (componentForm2[addressType]) {
            var val = place.address_components[i][componentForm2[addressType]];
            getLabelFor(addressType).className = "active"
            if (addressType == 'street_number') {
                document.getElementById(addressType).value = place.name
            } else {
                document.getElementById(addressType).value = val;
            }
            document.getElementById(fieldNames2[addressType] + "-error").style["display"] = "none";
            document.getElementById(addressType).style["borderBottom"] = "1px solid #9e9e9e"
        }
    }
    $('select').material_select();
    document.getElementById("billing-street_number").id = "billing-autocomplete"
}

// Bias the autocomplete object to the user's geographical location,
// as supplied by the browser's 'navigator.geolocation' object.
function geolocate2() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            var geolocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            var circle = new google.maps.Circle({
                center: geolocation,
                radius: position.coords.accuracy
            });
            autocomplete2.setBounds(circle.getBounds());
        });
    }
}
