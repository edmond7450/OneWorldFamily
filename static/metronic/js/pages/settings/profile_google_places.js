function initializeAutocomplete(id) {
    var element = document.getElementById(id);
    if (element) {
        var autocomplete = new google.maps.places.Autocomplete(element, {types: ['geocode']});
        autocomplete.setComponentRestrictions({'country': ['us', 'kz', 'bd']});
        google.maps.event.addListener(autocomplete, 'place_changed', onAddressChanged);
    }
}

function onAddressChanged() {
    var place = this.getPlace();
    // console.log(place);  // Uncomment this line to view the full object returned by Google API.

    for (var i in place.address_components) {
        var component = place.address_components[i];
        for (var j in component.types) {  // Some types are ["country", "political"]
            var type_element = document.getElementById(component.types[j]);
            if (type_element) {
                type_element.value = component.short_name; // component.long_name;
            }
        }
    }
    //document.forms[0].submit();

    validation.revalidateField('address');
    validation.revalidateField('postal_code');
}

google.maps.event.addDomListener(window, 'load', function () {
    initializeAutocomplete('address');
});

var input = document.getElementById('address');
google.maps.event.addDomListener(input, 'keydown', function (event) {
    if (event.keyCode === 13) {
        event.preventDefault();
    }
});