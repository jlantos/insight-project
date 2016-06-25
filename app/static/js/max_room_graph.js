function getDataroom() {
    $.get("/api/room_notification/100", function(graph) {
        console.log(graph.hottest_room_values)
	updateGraph_roommax(graph.hottest_room, graph.hottest_room_values)
    });
};


//setInterval(getData, 5000);


var WIDTH = 600
var    HEIGHT = 300
var    MARGINS = {
        top: 20,
        right: 20,
        bottom: 20,
        left: 20
    }

var svg = d3.select("#max_room_graph").insert("svg")
            .attr("width", WIDTH - MARGINS.right - MARGINS.left)
            .attr("height", HEIGHT - MARGINS.top - MARGINS.bottom);


$(window).load(getDataroom())

function updateGraph_roommax(room, data) {

  svg.selectAll(".line").remove();

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



  svg.append("svg:g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + (HEIGHT - MARGINS.bottom) + ")")
    .call(xAxis);
  svg.append("svg:g")
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
  svg.append('svg:path')
    .attr('d', lineGen(data))
    .attr('stroke', 'green')
    .attr('stroke-width', 2)
    .attr('fill', 'none');


}

