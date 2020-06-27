// stop form submit for address for, validate and send ajax req
$('#address-form').submit(function(e) {
    e.preventDefault(e);
    var url = "/shipping";
    var data = $(this).serialize();

    $("#address-loading").css("display", "inline-block");
    $("#address-submit").addClass("disabled");
    $("#loading-message").slideDown("slow");
    $.post(url, data, shippingCallback);
    return false;
});

// executes when address form is submitted via post
var shippingCallback = function (res) {
    $("#address-submit").removeClass("disabled");
    $("#address-loading").css("display", "none");
    $("#loading-message").css("display", "none");

    if (res.cartEmpty) {
        window.location.assign('/show/cart');
    }
    if (res.errors) {
        for (var key in res.errors) {
            $("#" + key + "-error").text(res.errors[key][0]);
            $("#" + key + "-error").show();
            $("#" + key + "-error").text(res.errors[key][0]);
            $("#" + key).css({ 'background-color': '#f7d9d0', 'border-bottom': '2px solid #d84315'});
            $("#" + key).change(function(){
                $("#" + key).css({ 'background-color': '', 'border-bottom': '' });
            });
        };
    } else {
        if (res.shippingOptions) {
            var targetElementId = "shipping-input-target";
            $("#" + targetElementId).empty();
            for (var i = 0; i < res.shippingOptions.length; i++) {
                addShippingOptionTo(res.shippingOptions[i], targetElementId);
            }
            $(".shipping-option").bind("click", shippingSelectionHandler);
        }
        if (res.addressId) {
            $('#address_id').val(res.addressId);
        }
        changeTab("2", "1", "shipping");
    }
}

// add radio shipping option to target element
function addShippingOptionTo(opt, targetId) {
    var inputId = `choice-${opt.id}`;
    var labelText = `${opt.carrier_display} ${opt.service_type_display} $${opt.price}`;
    var containerId = "radio-target-wrapper" + opt.id;

    var containerObject = $("<div></div>")
        .attr("id", containerId)
        .addClass("input-field")
        .addClass("col")
        .addClass("s12");

    var inputObject = $("<input/>")
        .attr("id", inputId)
        .attr("name", "cost")
        .attr("type", "radio")
        .attr("data-carrier", opt.carrier)
        .addClass("shipping-option")
        .addClass("with-gap")
        .attr("data-service", opt.service_type)
        .val(opt.price);

    var labelObject = $("<label></label>")
        .text(labelText)
        .attr("for", inputId);

    $("#" + targetId).append(containerObject);
    $("#" + containerId).append(inputObject);
    $("#" + containerId).append(labelObject);
}

// executes when radio button is clicked
function shippingSelectionHandler() {

    var shipping = parseFloat($(this).val()),
    newCost = parseFloat(cost) + shipping;
 
    $('#order-amount').fadeOut(500, function () {
        $("#order-subtotal").text(newCost.toFixed(2));
    }).fadeIn(500);

    $("#shipping-error").slideUp("slow");
}

// stop shipping form from submitting, move to next tab
$('#shipping-form').submit(function (e) {
    e.preventDefault();
    var radios = document.forms["shipping-form"]["cost"];
    var value;
    var radio = validateRadios(radios);

    if (radio) {
        value = radio.value;
        var cost = parseFloat(value) + parseFloat(cost);
        
        // save carrier and service values
        $('#carrier').val(radio.attributes[3].value);
        $('#service').val(radio.attributes[5].value);

        changeTab("3", "2", "payment");
        $("#section3").closest("li").removeClass('disabled');
        $('ul.tabs').tabs('select_tab', 'payment');
        $("#section2").closest("li").addClass("disabled");
    } else {
        $("#shipping-error").slideDown("slow");
    }
    return false;
});

// used on shipping form submit to make sure user has selected a shipping option
var validateRadios = function (radios) {
    for (var i in radios) {
        if (radios[i].checked) {
            return radios[i];
        }
    }
    return null;
}