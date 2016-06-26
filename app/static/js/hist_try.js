function getData_for_room_hist() {
    $.get("/api/room_notification/100", function(graph) {
   //     console.log(graph)
        updateRoomGraphHist( graph.dose)
    });
};



setInterval(getData_for_room_hist, 5000);

var WIDTH = 600
var HEIGHT = 300

var MARGINS = {
      top: 20,
      right: 20,
      bottom: 20,
      left: 50
    }



var margin = {
      top: 20,
      right: 20,
      bottom: 20,
      left: 50
    }




var width = width - MARGINS.left - MARGINS.right;
var height = height - MARGINS.top - MARGINS.bottom;


var vis3 = d3.select("#room_histogram").insert("svg")
  .attr("width", WIDTH)
  .attr("height", HEIGHT).append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");;



function updateRoomGraphHist(data) {
//var data = d3.range(1000).map(d3.randomBates(10));

var formatCount = d3.format(",.0f");

var margin = {top: 10, right: 30, bottom: 30, left: 30},
    width = 600 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

var x = d3.scale.linear()
    .rangeRound([0, width]);

var bins = d3.histogram()
    .domain(x.domain())
    .thresholds(x.ticks(20))
    (data);

var y = d3.scale.linear()
    .domain([0, d3.max(bins, function(d) { return d.length; })])
    .range([height, 0]);

//var svg = d3.select("body").append("svg")
//    .attr("width", width + margin.left + margin.right)
//    .attr("height", height + margin.top + margin.bottom)
//  .append("g")
//    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var bar = svg.selectAll(".bar")
    .data(bins)
  .enter().append("g")
    .attr("class", "bar")
    .attr("transform", function(d) { return "translate(" + x(d.x0) + "," + y(d.length) + ")"; });

bar.append("rect")
    .attr("x", 1)
    .attr("width", x(bins[0].x1) - x(bins[0].x0) - 1)
    .attr("height", function(d) { return height - y(d.length); });

bar.append("text")
    .attr("dy", ".75em")
    .attr("y", 6)
    .attr("x", (x(bins[0].x1) - x(bins[0].x0)) / 2)
    .attr("text-anchor", "middle")
    .text(function(d) { return formatCount(d.length); });

svg.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x));

}
