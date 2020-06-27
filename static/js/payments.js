var newCost = 0;
// this retrieves the new csrf token after any form submission via ajax
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// changes country field id, this is required bc wrong id comes from django form, TODO: fix this
var c = document.getElementById("id_country")
c.id = "country"
c.className = "address-field"

// sets validation focus out event listeners to desired fields
var addressFields = document.getElementsByClassName("address-field");
for (field of addressFields) {
  field.addEventListener("focusout", function (e) {
    if (e.target.value == "") {
      $(`#${ e.target.name }-error`).css("display", "block");
      e.target.style['borderBottom'] = "2px solid #d84315"
    } else {
      $(`#${ e.target.name }-error`).css("display", "none");
      e.target.style['borderBottom'] = "1px solid #9e9e9e"
    }
  });
}

//expands address fields if billing address not the same as shipping address
$("#same-address").change(function(){
  $("#billing-fields").slideToggle("slow");
})

function switchLoader(visible) {
  if (visible) {
    $('#ovl').hide()
    $('#preloader').hide()
  } else {
    $('#ovl').show()
    $('#preloader').show()
  }
}
