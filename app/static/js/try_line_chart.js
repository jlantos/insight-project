function getData_for_room() {
    $.get("/api/room_notification/100", function(graph) {
        console.log(graph)
        updateRoomGraph( graph.hottest_room_values)
    });
};


setInterval(getData_for_room, 5000);

var WIDTH = 600
var HEIGHT = 600
var MARGINS = {
      top: 20,
      right: 20,
      bottom: 20,
      left: 30
    }



var svg = d3.select("#max_room_graph").insert("svg")
            .attr("width", width)
            .attr("height", height);



function updateRoomGraph(data) {
   
//        vis.selectAll(".path").remove();

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
            return xScale(d.year);
        })
        .y(function(d) {
            return yScale(d.sale);
        })
        .interpolate("basis");
    vis.append('svg:path')
        .attr('d', lineGen(data))
        .attr('stroke', 'green')
        .attr('stroke-width', 2)
        .attr('fill', 'none');
    
}

//InitChart();
