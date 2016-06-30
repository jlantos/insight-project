function getData_for_user_hist() {
    $.get("/api/user_notification/1000_100", function(graph) {
//        console.log(graph.dose_rates)
        updateUserGraphHist( graph.dose_rates)
    });
};

window.onload = getData_for_user_hist();

setInterval(getData_for_user_hist(), 5000);

var WIDTH = 600
var HEIGHT = 300
 
var MARGINS = {
      top: 50,
      right: 10,
      bottom: 30,
      left: 70
    }

var vis4 = d3.select("#user_histogram").insert("svg")
  .attr("width", WIDTH)
  .attr("height", HEIGHT);



function updateUserGraphHist(data) {
   
  vis4.selectAll(".axis").remove();
  vis4.selectAll(".label").remove();
  vis4.selectAll(".title").remove();
  vis4.selectAll(".line").remove();

  
  // Scale axes
  xScale = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right]).domain([d3.min(data, function(d) {
    return d.value;
  }), d3.max(data, function(d) {
    return d.value;
  })]),


  yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([0,
    d3.max(data, function(d) {
    return d.freq;
  })]),


  xAxis = d3.svg.axis()
    .scale(xScale),
  yAxis = d3.svg.axis()
     .scale(yScale)
  .orient("left");


  // Draw x axis  
  vis4.append("svg:g")
    .attr("class", "axis")
    .attr("transform", "translate(0," + (HEIGHT - MARGINS.top) + ")")
    .call(xAxis);

  vis4.append("text")      // text label for the x axis
    .attr("class", "label")
    .attr("x", WIDTH / 2 )
    .attr("y",  HEIGHT - 10 )
    .style("text-anchor", "middle")
    .text("dose value");

  // Draw y axis
  vis4.append("svg:g")
    .attr("class", "axis")
    .attr("transform", "translate(" + (MARGINS.left) + ",0)")
    .call(yAxis)
     
  vis4.append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", 10 ) // - MARGINS.left)
    .attr("x", 0 - (HEIGHT / 2))
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .text("sqrt(n)");

  // Title
  vis4.append("text")
    .attr("class", "title")
    .attr("x", (WIDTH / 2))
    .attr("y",  MARGINS.top/2)
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .text("User dose distruibution");


  // Draw line

  var lineGen = d3.svg.line()
    .x(function(d) {
    return xScale(d.value);
  })
    .y(function(d) {
    return yScale(d.freq);
  })
 .interpolate("linear");
 
  vis4.append('svg:path')
    .attr("class", "line")
    .attr('d', lineGen(data))
    .attr('stroke', 'blue')
    .attr('stroke-width', 2)
    .attr('fill', 'none');

}
