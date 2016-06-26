function getData_for_room() {
    $.get("/api/room_notification/100", function(graph) {
        console.log(graph)
        updateRoomGraph( graph.hottest_room_values)
    });
};


setInterval(getData_for_room, 1000);

var width = 600
var height = 300
 
var MARGINS = {
      top: 20,
      right: 20,
      bottom: 20,
      left: 50
    }

var WIDTH = width - MARGINS.left - MARGINS.right;
var HEIGHT = height - MARGINS.top - MARGINS.bottom;


var vis = d3.select("#max_room_graph").insert("svg")
  .attr("width", width)
  .attr("height", height);



function updateRoomGraph(data) {
   
  vis.selectAll(".line").remove();
  vis.selectAll(".axis").remove();
  vis.selectAll(".label").remove();



  xScale = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right]).domain([d3.min(data, function(d) {
    return d.year;
  }), d3.max(data, function(d) {
    return d.year;
  })]),
   

  yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([0, 
    1.2 * 1.2 * d3.max(data, function(d) {
    return d.sale;
  })]),


  xAxis = d3.svg.axis()
    .scale(xScale),
  yAxis = d3.svg.axis()
     .scale(yScale)
  .orient("left");
  

  // Draw x axis  
  vis.append("svg:g")
    .attr("class", "axis")
    .attr("transform", "translate(0," + (HEIGHT - MARGINS.bottom) + ")")
    .call(xAxis);

  vis.append("text")      // text label for the x axis
    .attr("class", "label")
    .attr("x", WIDTH / 2 )
    .attr("y",  HEIGHT + MARGINS.bottom)
    .style("text-anchor", "middle")
    .text("time");


  // Draw y axis
  vis.append("svg:g")
    .attr("class", "axis")
    .attr("transform", "translate(" + (MARGINS.left) + ",0)")
    .call(yAxis);

  vis.append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", 0) // - MARGINS.left)
    .attr("x", 0 - (HEIGHT / 2))
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .text("dose");

    
  // Draw line

  var lineGen = d3.svg.line()
    .x(function(d) {
    return xScale(d.year);
  })
    .y(function(d) {
    return yScale(d.sale);
  })
    .interpolate("basis");

  vis.append('svg:path')      
    .attr("class", "line")
    .attr('d', lineGen(data))
    .attr('stroke', 'blue')
    .attr('stroke-width', 2)
    .attr('fill', 'none');
    
}

//InitChart();
