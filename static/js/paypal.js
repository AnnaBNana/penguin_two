paypal.Button.render(
  {
    env: "production", // Or 'production',
    client: {
      sandbox:
        "Adg9O06PQRVmZpYW61GezSzDHXsEwZiEPZRAx2cBQ5XaUWwyeIlWUOeXuEKiMfPL3jhhpPIMAbSOHazQ",
      production: 
        "AeLNC6tjMpH3BANJJz7Q1CiPOeK5cS4sYxsWMzno1aEV7CGA59L-G-T7Xgfv4RZYg42PGS60pEwTerHY"
    },
    commit: true, // Show a 'Pay Now' button
    style: {
      label: "paypal",
      size: "responsive", // small | medium | large | responsive
      shape: "rect", // pill | rect
      color: "gold", // gold | blue | silver | black
      tagline: false
    },
    payment: function(data, actions) {
      return actions.payment.create({
        payment: {
          transactions: [
            {
              amount: { total: parseFloat(newCost), currency: "USD" }
            }
          ]
        }
      });
    },
    onAuthorize: function(data, actions) {
      return actions.payment.execute().then(function(payment) {
        console.log(payment);
        var url = "/create/order";
        var context = {
          method: "paypal",
          address: $("#address-form").serialize(),
          shipping: $("#shipping-form").serialize(),
          payment: JSON.stringify(payment)
        };
        $.post(url, context, function(res) {
          // show success message
          console.log(res);
          $(".checkout-container").html(res);
        });
      });
    },
    onCancel: function(data, actions) {
      console.log("buyer cancelled payment", data);
    },
    onError: function(err) {
      console.log("there was a payment error", err);
    }
  },
  "#paypal-button"
);
