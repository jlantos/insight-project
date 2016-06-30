function getData_for_user() {
         $.get("/api/user_notification/1000_100", function(graph) {
         updateUserGraph(graph.hottest_user, graph.hottest_user_values)
    });
};

window.onload = getData_for_user()
setInterval(getData_for_user, 5000);

var vis2 = d3.select("#max_user_graph").insert("svg")
  .attr("width", WIDTH)
  .attr("height", HEIGHT);


function updateUserGraph(user, data) {
   
  vis2.selectAll(".line").remove();
  vis2.selectAll(".axis").remove();
  vis2.selectAll(".label").remove();
  vis2.selectAll(".title").remove();

  xScale = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right]).domain([d3.min(data, function(d) {
    return d.time;
  }), d3.max(data, function(d) {
    return d.time;
  })]),

  yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([0, 
    1.2 * d3.max(data, function(d) {
    return d.dose;
  })]),

  xAxis = d3.svg.axis()
    .scale(xScale),
  yAxis = d3.svg.axis()
     .scale(yScale)
  .orient("left");
  
  // Draw x axis  
  vis2.append("svg:g")
    .attr("class", "axis")
    .attr("transform", "translate(0," + (HEIGHT - MARGINS.top) + ")")
    .call(xAxis);

  vis2.append("text")      // text label for the x axis
    .attr("class", "label")
    .attr("x", WIDTH / 2 )
    .attr("y",  HEIGHT - 10)
    .style("text-anchor", "middle")
    .text("time");

  // Draw y axis
  vis2.append("svg:g")
    .attr("class", "axis")
    .attr("transform", "translate(" + (MARGINS.left) + ",0)")
    .call(yAxis);

  vis2.append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", 10) // - MARGINS.left)
    .attr("x", 0 - (HEIGHT / 2))
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .text("dose");

  // Title
  vis2.append("text")
    .attr("class", "title")
    .attr("x", (WIDTH / 2))             
    .attr("y",  MARGINS.top/2)
    .attr("text-anchor", "middle")  
    .style("font-size", "16px")   
    .text("User " + user.toString() + " (maximum current dose)");

  // Draw line
  var lineGen = d3.svg.line()
    .x(function(d) {
    return xScale(d.time);
  })
    .y(function(d) {
    return yScale(d.dose);
  })
    .interpolate("basis");

  vis2.append('svg:path')      
    .attr("class", "line")
    .attr('d', lineGen(data))
    .attr('stroke', 'blue')
    .attr('stroke-width', 2)
    .attr('fill', 'none');
}
