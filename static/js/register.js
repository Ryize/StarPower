$(function() {
	$(".btn").click(function() {
		$(".form-signin").toggleClass("form-signin-left");
    $(".form-signup").toggleClass("form-signup-left");
    $(".frame").toggleClass("frame-long");
    $(".signup-inactive").toggleClass("signup-active");
    $(".signin-active").toggleClass("signin-inactive");
    $(".forgot").toggleClass("forgot-left");
    $(this).removeClass("idle").addClass("active");
	});
});
document.addEventListener('DOMContentLoaded', function() {
  // Функция отправки формы при нажатии Enter
  function submitOnEnter(event, formId) {
    if (event.keyCode === 13) { // 13 - код клавиши Enter
      document.getElementById(formId).submit();
      event.preventDefault(); // Предотвращаем дальнейшее распространение события
    }
  }

  // Добавляем слушатели к элементам формы входа
  var loginFormInputs = document.getElementById('loginForm').getElementsByTagName('input');
  for (var i = 0; i < loginFormInputs.length; i++) {
    loginFormInputs[i].addEventListener('keydown', function(event) {
      submitOnEnter(event, 'loginForm');
    });
  }

  // Добавляем слушатели к элементам формы регистрации
  var registerFormInputs = document.getElementById('registerForm').getElementsByTagName('input');
  for (var i = 0; i < registerFormInputs.length; i++) {
    registerFormInputs[i].addEventListener('keydown', function(event) {
      submitOnEnter(event, 'registerForm');
    });
  }
});