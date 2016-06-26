function getDataroom() {
    $.get("/api/room_notification/100", function(graph) {
        console.log(graph.hottest_room_values)
	updateGraph_roommax(graph.hottest_room, graph.hottest_room_values)
    });
};


//setInterval(getData, 5000);


var WIDTH = 600
var HEIGHT = 300
var MARGINS = {
        top: 50,
        right: 50,
        bottom: 50,
        left: 50
    }

var vis = d3.select("#max_room_graph").insert("svg")
            .attr("width", WIDTH - MARGINS.right - MARGINS.left)
            .attr("height", HEIGHT - MARGINS.top - MARGINS.bottom);


$(window).load(getDataroom())

function updateGraph_roommax(room, data) {

  vis.selectAll(".line").remove();
  vis.selectAll(".x_axis").remove();
  vis.selectAll(".y_axis").remove();
  vis.selectAll(".label".remove(); 

  // Recalc axis limits
  xScale = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right]).domain([d3.min(data, function(d) {
        return d.time_string;}), d3.max(data, function(d) {
                            return d.time_string;
                        })]),

//  console.log(data.time)
  yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([d3.min(data, function(d) {
                            return d.dose_string;
                        }), d3.max(data, function(d) {
                            return d.dose_string;
                        })]),
  
  xAxis = d3.svg.axis()
  .scale(xScale),

  yAxis = d3.svg.axis()
  .scale(yScale)
  .orient("left");


  // Draw x axis
  vis.append("svg:g")
    .attr("class", "x_axis")
    .attr("transform", "translate(0," + (HEIGHT - MARGINS.bottom) + ")")
    .call(xAxis);

  vis.append("text")      // text label for the x axis
    .attr("class", "label")
    .attr("x", WIDTH / 2 )
    .attr("y",  HEIGHT + MARGIN.bottom)
    .style("text-anchor", "middle")
    .text("time");


  // Drax y axis
  vis.append("svg:g")
    .attr("class", "y_axis")
    .attr("transform", "translate(" + (MARGINS.left) + ",0)")
    .call(yAxis);


  vis.append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 – MARGIN.left)
    .attr("x",0 - (HEIGHT / 2))
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .text("Dose");


  // Draw line
  var lineGen = d3.svg.line()
    .x(function(d) {
        return xScale(d.time);
    })
    .y(function(d) {
        return yScale(d.dose_rate);
    })
    .interpolate("basis");  

  vis.append('svg:path')
    .attr('d', lineGen(data))
    .attr('stroke', 'green')
    .attr('stroke-width', 2)
    .attr('fill', 'none');

}

