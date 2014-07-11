(function($) {
    $.fn.geosearch = function(options) {
      this.each(function() {
        var autocomplete = new google.maps.places.Autocomplete(this);
        google.maps.event.addListener(autocomplete, 'place_changed', function() {
            var place = autocomplete.getPlace();
            if (!place.geometry)
                return;
            var url = "http://geosearch-anandology.rhcloud.com/geosearch?lat=" + place.geometry.location.lat() + "&lon=" + place.geometry.location.lng();
            console.log(place.geometry.location);
            $.getJSON(url, function(response) {
              if (response) {
                if (options.success)
                  options.success(response);
              }
              else {
                if (options.error) 
                  options.error();
              }
              console.log(response);
            });
        });
      });
      //
    }
}(jQuery));
