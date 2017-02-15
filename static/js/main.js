$(document).ready(function() {
  var loc = location.pathname;
  if (loc.startsWith('/shop/')) {
    $('.shop').addClass('active');
  }
  else if (loc.startsWith('/learn/')) {
    $('.learn').addClass('active');
  }
  else if (loc.startsWith('/blog/')) {
    $('.blog').addClass('active');
  }
});
