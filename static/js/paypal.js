paypal.Button.render(
  {
    env: "production", // Or 'sandbox',
    client: {
      production: "wx6zjy2zwskxdbn4$ecd4c83a3f227db6881f5c2816c22796",
      sandbox: "d4zk9xdbrvrqcfkg$4efca6c52781660bd41305709b3f4f4f"
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
