function getData_for_room_alert() {
    $.get("/api/room_notification/100", function(graph) {
       myFunction(graph.alerts)
    });
};

setInterval(getData_for_room_alert, 10000);


function myFunction(response) {
    var arr = (response);
    var i;
    var out = "<table style=\"width:100%\">";

    out += "<tr><th>Time</th><th>Room</td><th>Users</th> </tr>"

    for(i = 0; i < arr.length; i++) {
        out += "<tr><td>" +
        arr[i].alert_time.toString() + 
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
