var newCost;
// checkout navigation
$("#back-to-address").click(function () {
  changeTab("1", "2", "delivery")
});

$("#back-to-shipping").click(function () {
  changeTab("2", "3", "shipping");
});

// helper function to change which tab is shown in checkout process
function changeTab(target, current, target_name) {
  $("#section" + target).closest("li").removeClass('disabled');
  $('ul.tabs').tabs('select_tab', target_name);
  $("#section" + current).closest("li").addClass("disabled");
  $("#address-err").css("display", "none");
}

// listener for shipment rates radio button clicks
$(".shipping-radio").bind("click", handler);

// toggle card options only if card selected by user. Hide when paypal is selected
$(".cc-btn").click(function(){
  $(".card-options").slideToggle("fast");
});

// executes when radio button is clicked
function handler() {
  var shipping = parseFloat($(this).val());
  newCost = parseFloat(cost) + shipping;
  $('#order-amount').fadeOut(500, function () {
    $("#order-subtotal").text(newCost.toFixed(2));
  }).fadeIn(500);
  $("#shipping-error").slideUp("slow");
}

function addRadio(type, displayName, rate, carrier, service) {
  $("#" + type + "-wrapper").show();
  $("." + type + "-value").html("$" + rate);
  $("." + type).val(rate);
  $("#" + type + "-label").html(displayName).css("text-transform", "capitalize");
  $("." + type).attr("data-carrier", carrier);
  $("." + type).attr("data-service", service);
}

// executes when address form is submitted via post
var callback = function(res){
  console.log("response object:", res);
  if (res.cart_empty) {
    window.location.assign('/show/cart');
  }
  if (res.address_id) {
    $("#address_id").val(res.address_id);
  }
  if (res.all_options) {
    var rate,
    shipment = JSON.parse(res.all_options),
    country = shipment.to_address.country,
    uspsShipment = JSON.parse(res.usps_shipment),
    fedexShipment = JSON.parse(res.fedex_shipment),
    orderSubtotal = res.order_subtotal, 
    type, displayName, rate, carrier, service;
    console.log("this is the shipment:", shipment);
    console.log("fedex shipment", fedexShipment)
    console.log("usps shipment:", uspsShipment);
    if (uspsShipment) {
      type = "usps-low";
      displayName = "USPS Flat Rate:";
      rate = uspsShipment.rates[0].rate;
      carrier = uspsShipment.rates[0].carrier;
      service = uspsShipment.rates[0].service;
      addRadio(type, displayName, rate, carrier, service) 
    }
    if (fedexShipment) {
      var ratesArray = fedexShipment.rates,
      fedexLow = fedexShipment.rates[ratesArray.length - 1]
      type = "fedex-low";
      displayName = fedexLow.service.replace(/_/g, " ").toLowerCase() + ":";
      rate = fedexLow.rate;
      carrier = fedexLow.carrier;
      service = fedexLow.service;
      addRadio(type, displayName, rate, carrier, service);
      fedexHigh = fedexShipment.rates[ratesArray.length - 2]
      type = "fedex-high";
      displayName = fedexHigh.service.replace(/_/g, " ").toLowerCase() + ":";
      rate = fedexHigh.rate;
      carrier = fedexHigh.carrier;
      service = fedexHigh.servide
      addRadio(type, displayName, rate, carrier, service);
    }
    if (shipment) {
      for (var i = 0; i < shipment.rates.length; i++) {
        current = shipment.rates[i]
        uspsLow = (current.service == "Priority" || current.service == "FirstClassPackageInternationalService") && current.carrier == "USPS"
        uspsHigh = (current.service == "Express" || current.service == "PriorityMailInternational") && current.carrier == "USPS"
        fedexLow = (current.service == "GROUND_HOME_DELIVERY" || current.service == "INTERNATIONAL_ECONOMY") && current.carrier == "FedEx"
        fedexHigh = (current.service == "FEDEX_2_DAY" || current.service == "INTERNATIONAL_PRIORITY") && current.carrier == "FedEx"
        if (uspsHigh) {
          type = "usps-high"
          displayName = "USPS Express:";
          rate = current.rate;
          carrier = current.carrier;
          service = current.service;
          addRadio(type, displayName, rate, carrier, service);
        }
        if (!uspsShipment && !fedexShipment) {
          if (uspsLow) {
            type = "usps-low"
            displayName = "USPS Priority:";
            rate = current.rate;
            carrier = current.carrier;
            service = current.service;
            addRadio(type, displayName, rate, carrier, service);
          }
          else if (fedexLow) {
            // TODO: NOTE THAT LAST 2 OPTIONS ARE FEDEX
            type = "fedex-low"
            displayName = current.carrier + " " + current.service.replace(/_/g, " ").toLowerCase() + ":";
            rate = current.rate;
            carrier = current.carrier;
            service = current.service;
            addRadio(type, displayName, rate, carrier, service);
          }
          else if (fedexHigh) {
            type = "fedex-high"
            displayName = current.carrier + " " + current.service.replace(/_/g, " ").toLowerCase() + ":";
            rate = current.rate;
            carrier = current.carrier;
            service = current.service;
            addRadio(type, displayName, rate, carrier, service);
          }
        }
      }
    }
    var address = shipment.to_address;
    var street1 = $("#autocomplete").val();
    var street2 = $("#apt").val();
    var countryName = $("#country").val();
    $("#billing-name").val(address.name);
    getLabelFor("billing-name").className = "active"
    $("#billing-street").val(street1);
    getLabelFor("billing-street").className = "active"
    $("#billing-apt").val(street2);
    getLabelFor("billing-apt").className = "active"
    $("#billing-city").val(address.city);
    getLabelFor("billing-city").className = "active"
    $("#billing-state").val(address.state);
    getLabelFor("billing-state").className = "active"
    $("#billing-zip").val(address.zip);
    getLabelFor("billing-zip").className = "active"
    $("#id_address_country").val(address.country);
    $("#id_address_country").val(countryName);
    $('select').material_select();
  }
  if (res.errors) {
    console.log("there are errors:",res.errors);
    for (var i in res.errors) {
      // console.log("the errors:", res.errors[i])
      // console.log("the error field:", res.errors[i].field)
      switch (res.errors[i].field){
        case "email":
          // console.log("there was an email error");
          $("#email-error").html(res.errors[i].message).css("display", "block");
          $("#email").css("border-bottom", "2px solid #d84315");
          break;
        case "street1":
          console.log("what?")
          $("#street-error").html(res.errors[i].message).css("display", "block");
          $("#autocomplete").css("border-bottom", "2px solid #d84315");
          break;
        case "street2":
          $("#apt-error").html(res.errors[i].message).css("display", "block");
          $("#apt").css("border-bottom", "2px solid #d84315");
          break;
        case "city":
          $("#city-error").html(res.errors[i].message).css("display", "block");
          $("#city").css("border-bottom", "2px solid #d84315");
          break;
        case "state":
          $("#state-error").html(res.errors[i].message).css("display", "block");
          $("#administrative_area_level_1").css("border-bottom", "2px solid #d84315");
        case "zip":
          $("#zip_code-error").html(res.errors[i].message).css("display", "block");
          $("#postal_code").css("border-bottom", "2px solid #d84315");
        case "address":
          $("#address-error").html(res.errors[i].message).css({"display": "block", "font-size": "1em"});
          break;
        default:
          break;
      }
    }
  } else { // success, do not need to display errors, move on to next section
    changeTab("2", "1", "shipping");
  }
  // stop loading message/spinner
  $("#address-loading").css("display", "none");
  $("#address-submit").removeClass("disabled");
  $("#loading-message").css("display", "none");
}

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

// hijack form submit for address for, validate and move on
$('#address-form').submit(function(e){
  e.preventDefault();
  var url = "/shipping_cost"
  var data = $(this).serialize();
  $("#address-loading").css("display", "inline-block");
  $("#address-submit").addClass("disabled");
  $("#loading-message").slideDown("slow");
  $.post(url, data, callback);
  // refreshing csrf token
  var csrftoken = getCookie('csrftoken');
  $("[name=csrfmiddlewaretoken]").val(csrftoken);
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
  return false;
});

// stop shipping form from submitting, move to next tab
$('#shipping-form').submit(function(e){
  e.preventDefault();
  var radios = document.forms["shipping-form"]["shipping"];
  var value;
  // console.log(radios)
  if (validateRadios(radios)){
    for (var i in radios) {
      if (radios[i].checked) {
        value = radios[i].value;
        radioID = radios[i].id;
        var carrier = $("#" + radioID).attr("data-carrier")
        var service = $("#" + radioID).attr("data-service")
        console.log("carrier and service:", carrier, service)
        $("#carrier").val(carrier);
        $("#service").val(service);
      }
    }
    changeTab("3", "2", "payment");
    $("#section3").closest("li").removeClass('disabled');
    $('ul.tabs').tabs('select_tab', 'payment');
    $("#section2").closest("li").addClass("disabled");
    var cost = parseFloat(value) + parseFloat(cost);
  } else {
    $("#shipping-error").slideDown("slow");
  }
  return false;
});

// used on shipping form submit to make sure user has selected a shipping option
var validateRadios = function(radios) {
  for (var i in radios){
    if (radios[i].checked){
      return true;
    } 
  }
  return false;
}

// changes country field id
var c = document.getElementById("id_country")
c.id = "country"
c.className = "ad-field"

// sets validation focus out event listeners to desired fields
var adFields = document.getElementsByClassName("ad-field");
// console.log(adFields)
for (field of adFields) {
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
    // var valid = validate_form();
    // console.log(valid);
    var cardData = getCardData();
    stripe.createToken(card, cardData).then(function(result) {
      console.log("RESULT RESPONSE::::>", result);
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
    // Submit the form
    // must gather data from other forms first, send it along to a custom route with ajax
    var url = "/create/order"
    data = {
      "method": "card",
      "address": $("#address-form").serialize(),
      "shipping": $("#shipping-form").serialize(),
      "payment": $("#payment-form").serialize()
    }
    console.log(data['shipping'])
    $.post(url, data, function(res){
      if (res.error) {
        console.log(res.error)
        $("#checkout-err").html(res.error);
        $("#checkout-err").css("display", "block");
      } else {
        $(".checkout-container").html(res);
      }
      console.log("this is the final server response:", res);
      // check for errors
      // if errors, display them
      // else 
      // show success message
      // success page can have some links to articles
      // how to manage this content
    });
  }

  function getCardData(){
    // if 
    var data = {}
    console.log("SERIALIZED DATA", $("#payment-form").serializeArray());
    var formData = $("#payment-form").serializeArray();
    for (var f in formData) {
      if (formData[f].name != "csrfmiddlewaretoken" && formData[f].name != "same_address") {
        data[formData[f].name] = formData[f].value;
      }
    }
    console.log("CLEANED:", data);
    return data;
  }


