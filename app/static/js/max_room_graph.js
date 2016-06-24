function getData() {
    $.get("/api/room_notification/100", function(graph) {
        console.log(graph)
	updateGraph(graph.hottest_room, graph.hottest_room_values)
    });
};


setInterval(getData, 15000);


var WIDTH = 600
    HEIGHT = 600
    MARGINS = {
        top: 20,
        right: 20,
        bottom: 20,
        left: 20
    },

var svg = d3.select("max_room_graph").insert("svg")
            .attr("width", WIDTH - MARGINS.right - MARGINS.left)
            .attr("height", HEIGHT - MARGINS.top - MARGINS.bottom);


function updateGraph(room, data) {

  svg.selectAll(".line").remove();

  xScale = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right]).domain([d3.min(data, function(d) {
        return d.time;}), d3.max(data, function(d) {
                            return d.time;
                        })]),


  yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([d3.min(data, function(d) {
                            return d.dose_rate;
                        }), d3.max(data, function(d) {
                            return d.dose_rate;
                        })]),
  
  xAxis = d3.svg.axis()
  .scale(xScale),

  yAxis = d3.svg.axis()
 .scale(yScale)
 .orient("left");



  vis.append("svg:g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + (HEIGHT - MARGINS.bottom) + ")")
    .call(xAxis);
  vis.append("svg:g")
    .attr("class", "y axis")
    .attr("transform", "translate(" + (MARGINS.left) + ",0)")
    .call(yAxis);
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
