function getData_for_room_alert() {
    $.get("/api/room_notification/100", function(graph) {
       // console.log(graph.dose_rates)
       // updateRoomAlert(graph.alerts)
       myFunction(graph.avg_time, graph.alerts)
    });
};


setInterval(getData_for_room_alert, 1000);



function myFunction(alert_time, response) {
    var time = alert_time
    var arr = (response);
    var i;
    var out = "<table style=\"width:100%\">";

    out += "<tr><th>Time</th><th>Room</td><th>Users</th> </tr>"

    for(i = 0; i < arr.length; i++) {
        out += "<tr><td>" +
        time.toString() + 
        "</td><td>" +
        arr[i].room +
        "</td><td>" +
        users_to_string(arr[i].users_to_alert) +
        "</td></tr>";
    }
    out += "</table>";
    document.getElementById("id01").innerHTML = out;
}

function users_to_string(user_list) {
   var user_str = '';

   for(i = 0; i < user_list.length-1; i++) {
     user_str += user_list[i] + ', ';

     if (i%10 == 0) {
      user_str += '\n'
     }
  } 
  user_str += user_list[i];
  return(user_str)
}
