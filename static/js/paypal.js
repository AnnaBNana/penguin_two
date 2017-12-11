paypal.Button.render({
    env: 'sandbox', // Or 'production',
    client: {
        sandbox: "AeCoyZ5UE9IIRs60YxlTHGP06ULpgj_XnoaZoNyVudpoED5_RmLeKlBYvDko3pvyXeKqXU78a2cGn2Ux"
    },
    commit: true, // Show a 'Pay Now' button
    style: {
        label: 'paypal',
        size: 'responsive',    // small | medium | large | responsive
        shape: 'rect',     // pill | rect
        color: 'gold',     // gold | blue | silver | black
        tagline: false
    },
    payment: function (data, actions) {
        return actions.payment.create({
            payment: {
                transactions: [
                    {
                        amount: { total: parseFloat(newCost), currency: 'USD' }
                    }
                ]
            }
        });
    },
    onAuthorize: function (data, actions) {
        return actions.payment.execute().then(function (payment) {
            console.log(payment)
            var url = "/create/order"
            var context = {
                "method": "paypal",
                "address": $("#address-form").serialize(),
                "shipping": $("#shipping-form").serialize(),
                "payment": JSON.stringify(payment)
            }
            $.post(url, context, function(res){
                // show success message
                console.log(res);
                $(".checkout-container").html(res);
            })
        });
    },
    onCancel: function (data, actions) {
        console.log("buyer cancelled payment", data);
    },
    onError: function (err) {
        console.log("there was a payment error", err);
    }

}, '#paypal-button');
