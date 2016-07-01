function getData_for_room_hist() {
        $.get("/api/room_notification/100", function(graph) {
        updateRoomGraphHist( graph.dose_rates)
    });
};


window.onload = getData_for_room_hist();
setInterval(getData_for_room_hist, 2000);

var vis3 = d3.select("#room_histogram").insert("svg")
  .attr("width", WIDTH)
  .attr("height", HEIGHT);



function updateRoomGraphHist(data) {
   
  vis3.selectAll(".axis").remove();
  vis3.selectAll(".label").remove();
  vis3.selectAll(".title").remove();
  vis3.selectAll(".line").remove();
  
  // Scale axes
  xScale = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right]).domain([d3.min(data, function(d) {
    return d.value;
  }), d3.max(data, function(d) {
    return d.value;
  })]),

  yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([0,
    1.2 * d3.max(data, function(d) {
    return d.freq;
  })]),

  xAxis = d3.svg.axis()
    .scale(xScale),
  yAxis = d3.svg.axis()
     .scale(yScale)
  .orient("left");

  // Draw x axis  
  vis3.append("svg:g")
    .attr("class", "axis")
    .attr("transform", "translate(0," + (HEIGHT - MARGINS.top) + ")")
    .call(xAxis);

  vis3.append("text")      // text label for the x axis
    .attr("class", "label")
    .attr("x", WIDTH / 2 )
    .attr("y",  HEIGHT - 10)
    .style("text-anchor", "middle")
    .text("dose value");

  // Draw y axis
  vis3.append("svg:g")
    .attr("class", "axis")
    .attr("transform", "translate(" + (MARGINS.left) + ",0)")
    .call(yAxis);

  vis3.append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", 0) // - MARGINS.left)
    .attr("x", 0 - (HEIGHT / 2))
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .text("sqrt(n)");

  // Title
  vis3.append("text")
    .attr("class", "title")
    .attr("x", (WIDTH / 2))
    .attr("y",  MARGINS.top/2)
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .text("Room dose distruibution");

  // Draw line
  var lineGen = d3.svg.line()
    .x(function(d) {
    return xScale(d.value);
  })
    .y(function(d) {
    return yScale(d.freq);
  })
 .interpolate("linear");
 
  vis3.append('svg:path')
    .attr("class", "line")
    .attr('d', lineGen(data))
    .attr('stroke', 'blue')
    .attr('stroke-width', 2)
    .attr('fill', 'none');

}
