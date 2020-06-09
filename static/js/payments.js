var newCost = 0;

// toggle card options only if card selected by user. Hide when paypal is selected
$(".cc-btn").click(function(){
  $(".card-options").slideToggle("fast");
});

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

// STRIPE //
var stripe = Stripe('pk_test_FMSbuQaOxYqZhILgBHxVWDOq');
var elements = stripe.elements();

  // Custom styling can be passed to options when creating an Element.
var style = {
  base: {
    // Add your base input styles here. For example:
    color: '#32325D',
    fontWeight: 500,
    fontSize: '16px',
    fontSmoothing: 'antialiased',
  }
};
// Create an instance of the card Element
var card = elements.create('card', {style: style});
// Add an instance of the card Element into the `card-element` <div>
card.mount('#card-element');

card.addEventListener('change', function(event) {
  var displayError = document.getElementById('card-errors');
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = '';
  }
});

// Create a token or display an error when the form is submitted.
var form = document.getElementById('payment-form');
form.addEventListener('submit', function(event) {
  event.preventDefault();
  var cardData = getCardData();
  stripe.createToken(card, cardData).then(function(result) {
    if (result.error) {
      // Inform the user if there was an error
      var errorElement = document.getElementById('card-errors');
      errorElement.textContent = result.error.message;
    } else {
      // Send token to server
      stripeTokenHandler(result.token);
    }
  });
});

function stripeTokenHandler(token) {
  // Insert the token ID into the form so it gets submitted to the server
  var form = document.getElementById('payment-form');
  var hiddenInput = document.createElement('input');
  hiddenInput.setAttribute('type', 'hidden');
  hiddenInput.setAttribute('name', 'stripeToken');
  hiddenInput.setAttribute('value', token.id);
  form.appendChild(hiddenInput);

  var url = "/create/order"
  data = {
    "method": "card",
    "address": $("#address-form").serialize(),
    "shipping": $("#shipping-form").serialize(),
    "payment": $("#payment-form").serialize()
  }
  switchLoader(false);
  fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'content-type': 'application/json'
    },
    body: JSON.stringify(data)
  }).then(function (response) {
    switchLoader(true);
    if (!response.ok) {
      throw Error(response.statusText);
    }
    return response.text();
  }).then(function (response) {
    if (response.error) {
      $("#checkout-err").html(response.error);
      $("#checkout-err").css("display", "block");
    } else {
      $(".checkout-container").html(response);
    }
  }).catch(function (error) {
    errorMsg = "There was an error with our service. Please contact <a href='mailto:rickpropas@comcast.net'>rickpropas@comcast.net</a>"
    $("#checkout-err").html(errorMsg);
    $("#checkout-err").css("display", "block");
  });
}

function getCardData(){
  var data = {}
  var formData = $("#payment-form").serializeArray();
  for (var f in formData) {
    if (formData[f].name != "csrfmiddlewaretoken" && formData[f].name != "same_address") {
      data[formData[f].name] = formData[f].value;
    }
  }
  return data;
}

function switchLoader(visible) {
  if (visible) {
    $('#ovl').hide()
    $('#preloader').hide()
  } else {
    $('#ovl').show()
    $('#preloader').show()
  }
}
