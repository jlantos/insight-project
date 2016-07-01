function getData_for_user_alert() {
         $.get("/api/user_notification/1000_100", function(graph) {
         myFunction2(graph.alerts)
    });
};


setInterval(getData_for_user_alert, 5000);


function myFunction2(response) {
    var arr = response;
    var i;
    var out = "<table style=\"width:100%\">";

    out += "<tr><th>Time</th><th>User in danger</td><th>Closest colleague</th><th>Distance</th> </tr>"

    for(i = 0; i < arr.length; i++) {
        out += "<tr><td>" +
        arr[i].alert_time.toString() + 
        "</td><td>" +
        arr[i].user_in_danger +
        "</td><td>" +
        arr[i].user_to_alert +
        "</td><td>" +
        arr[i].distance +
        "</td></tr>";
    }
    out += "</table>";
    document.getElementById("id00").innerHTML = out;
}

