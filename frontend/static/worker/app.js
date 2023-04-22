var startCountdownTime = new Date().getTime();

var x = setInterval(function() {

  var now = new Date().getTime();
    
  var reminderMinutes = 5;
  var countDownTime = new Date(startCountdownTime + (reminderMinutes*60*1000));

  var distance = countDownTime - now;

  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  document.getElementById("timer").innerHTML = minutes + "m " + seconds + "s ";

  if (distance < 0) {
    clearInterval(x);
    document.getElementById("timer").innerHTML = "Time's Out";
    window.alert("Please refresh waiting time!");

  }
}, 1000);



