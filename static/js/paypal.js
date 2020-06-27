paypal.Buttons({
  createOrder: function (data, actions) {
    data = JSON.stringify({
      "method": "paypal",
      "address": $("#address-form").serialize(),
      "shipping": $("#shipping-form").serialize(),
      "payment": ""
    })
    return fetch('/create/order', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'content-type': 'application/json'
      },
      body: data,
      credentials: 'same-origin'
    }).then(function (res) {
      return res.json();
    }).then(function (data) {
      if (data.cart_empty) {
        window.location.assign('/show/cart');
      }
      return data.id;
    })
    // .catch(function(error) {
    //   console.log("error");
    //   console.log(error)
    // });
  },
  onApprove: function (data, actions) {
    // Authorize the transaction
    switchLoader(false);
    actions.order.authorize().then(function (authorization) {

      // Get the authorization id
      var authorizationID = authorization.purchase_units[0]
        .payments.authorizations[0].id

      // Call your server to validate and capture the transaction
      return fetch('/capture/order', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'content-type': 'application/json'
        },
        body: JSON.stringify({
          orderID: data.orderID,
          authorizationID: authorizationID
        })
      }).then(function (response) {
        switchLoader(true);
        if (!response.ok) {
          throw Error(response.statusText);
        }
        return response.text()
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
    });
  },
  // onError: function (err) {
  //   console.log(err)
  //   console.log('err!!!!')
  // }
}).render('#paypal-button');
