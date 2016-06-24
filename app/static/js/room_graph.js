<script language="javascript">
var graph = {{jsondata | safe}};
console.log(graph);
</script>


<script src="//d3js.org/d3.v3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>
<script>
window.onload = function() {
var width = 600,
    height = 600;

var svg = d3.select("#graph_div").append("svg")
    .attr("width", width)
    .attr("height", height);

// White to red
var color = d3.scale.linear().domain([0, 150]).range(['#ffffff', '#9b0017']);

var force = d3.layout.force()
    .charge(-120)
    .linkDistance(30)
    .size([width, height]);

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var graph = {{ jsondata | safe  }};


force.nodes(graph.nodes)
     .links(graph.links)
     .start();

var link = svg.selectAll(".link")
      .data(graph.links)
    .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", 1);

var node = svg.selectAll(".node")
      .data(graph.nodes)
    .enter().append("circle")
      .attr("class", "node")
      .attr("r", 8)
      .style("fill", function(d) { return color(d.dose); })
      .call(force.drag);

node.append("title")
      .text(function(d) { return (d.name).toString().concat(': ', d.dose); });

force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
});
}
</script>
