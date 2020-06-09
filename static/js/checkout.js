// checkout navigation
// navigate from shipping to address
$("#back-to-address").click(function () {
    changeTab("1", "2", "delivery")
});
// navigate from payment to shipping
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
