

function world_or_us_map(selected_ids, json_urlbase, us_only) {
  var width = 480,
     height = 240;
  var projection, data_url;

  if (us_only) {
    projection = d3.geo.albersUsa()
        .scale(500)
        .translate([width / 2, height / 2]);

    data_url = json_urlbase + 'us.json';
  } else {
    projection = d3.geo.equirectangular()
        .scale(80)
        .translate([width / 2, height / 2]);

    data_url = json_urlbase + 'world-50m.json';
  }

  var path = d3.geo.path()
      .projection(projection);

  var svg = d3.select(".map").append("svg")
    .attr("width", width)
    .attr("height", height);

  d3.json(data_url, function(error, data) {
     svg.insert("path", ".graticule")
        .datum(topojson.feature(data, data.objects.land))
        .attr("class", "land")
        .attr("d", path);

  var regions, mesh_data;
  if (us_only) {
    regions = topojson.feature(data, data.objects.states).features;
    mesh_data = data.objects.states;
  } else {
    regions = topojson.feature(data, data.objects.countries).features;
    mesh_data = data.objects.countries;
  }

  svg.selectAll(".region")
      .data(regions)
    .enter().insert("path", ".graticule")
      .attr("class", function(d, i) {
        if (selected_ids.indexOf(d.id) > -1) { return 'region selected'; }
        else { return 'region'; }
       })
      .attr("d", path);

  svg.insert("path", ".graticule")
      .datum(topojson.mesh(data, mesh_data, function(a, b) { return a !== b; }))
      .attr("class", "region-boundary")
      .attr("d", path);

  });  // end d3.json

}

function world_map(selected_ids, json_urlbase) {
  return world_or_us_map(selected_ids, json_urlbase, false);
}

function us_map(selected_ids, json_urlbase) {
  return world_or_us_map(selected_ids, json_urlbase, true);
}