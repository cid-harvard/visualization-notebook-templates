from IPython.core.display import display_html, display, HTML, Javascript
import json
import random
import pandas as pd
import csv

import os
path = os.path.dirname(__file__)

class VisTkViz(object):

    JS_LIBS = ['https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js',
               #'https://cdnjs.cloudflare.com/ajax/libs/queue-async/1.0.7/queue.min.js',
               'http://127.0.0.1/rv/Dev/vis-toolkit/js/topojson.js',
               'http://127.0.0.1/rv/Dev/vis-toolkit/build/vistk.js']
               #'http://cid-harvard.github.io/vis-toolkit/build/vistk.js']

    def create_container(self):
        container_id = "vistk_div_{id}".format(id=random.randint(0, 100000))
        container = """<div id='{id}' style='height:auto;'></div>"""\
            .format(id=container_id)
        display(HTML(container))
        return container_id

    def handle_data(self, data):
        if type(data) == list and len(data) > 0 and type(data[0]) == dict:
            return json.dumps(data)
        elif type(data) == pd.DataFrame:
            return data.to_json(orient="records")
        else:
            raise ValueError()

    def validate_data(self, data):
        raise NotImplementedError()

    def preprocess_data(self, data):
        return data

    def draw(self, data):
        self.container_id = self.create_container()
        data = self.preprocess_data(data)
        json_data = self.handle_data(data)
        self.draw_viz(json_data)

    def draw_viz(self, json_data):
        raise NotImplementedError()


class Treemap(VisTkViz):

    def __init__(self, id='id', group='group', name=None, color=None, size=None, year=1995, filter=None, sort=None):
        super(Treemap, self).__init__()

        self.id = id
        self.group = group
        self.year = year
        self.sort = sort

        if name is None:
            self.name = id
        else:
            self.name = name

        if color is None:
            self.color = id
        else:
            self.color = color

        if size is None:
            self.size = id
        else:
            self.size = size

        if filter is None:
            self.filter = '[]'
        else:
            self.filter = filter

    def draw_viz(self, json_data):

        js = """
        (function (){

          var viz_data = %s;
          var viz_container = '#%s';

          var visualization = vistk.viz()
                .params({
                  type: 'treemap',
                  container: viz_container,
                  height: 600,
                  width: 900,
                  data: viz_data,
                  var_id: '%s',
                  var_sort: '%s',
                  var_group: '%s',
                  var_color: '%s',
                  var_size: '%s',
                  var_text: '%s',
                  time: {
                    var_time: 'year',
                    current_time: %s
                  }
                });

            d3.select(viz_container).call(visualization);
        })();
        """ % (json_data, self.container_id, self.id, self.sort, self.group, self.color, self.size,
               self.name, self.year)

        display(Javascript(lib=self.JS_LIBS, data=js))


class Scatterplot(VisTkViz):

    def __init__(self, x="x", y="y", id="id", r="r", name=None, color=None, year=2013):
        super(Scatterplot, self).__init__()
        self.id = id
        self.x = x
        self.y = y
        self.r = r
        self.year = year

        if name is None:
            self.name = id
        else:
            self.name = name

        if color is None:
            self.color = id
        else:
            self.color = color

    def draw_viz(self, json_data):

        js = """
        (function (){

          var viz_data = %s;
          var viz_container = '#%s';

          var visualization = vistk.viz()
            .params({
              type: 'scatterplot',
              width: 800,
              height: 600,
              margin: {top: 10, right: 10, bottom: 30, left: 30},
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_group: 'continent',
              var_color: '%s',
              var_x: '%s',
              var_y: '%s',
              var_r: '%s',
              var_text: 'name',
              time: {
                var_time: 'year',
                current_time: %s,
                parse: function(d) { return d; }
              }
            });

        d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.color, self.x, self.y, self.r, self.year)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Dotplot(VisTkViz):

    def __init__(self, x="x", id="id", color="color", name=None, group=None, year=2013):
        super(Dotplot, self).__init__()
        self.id = id
        self.x = x
        self.year = year
        self.color = color

        if group is None:
            self.group = id
        else:
            self.group = group

        if name is None:
            self.name = id
        else:
            self.name = name

    def draw_viz(self, json_data):

        js = """
        (function (){

          var viz_data = %s;
          var viz_container = '#%s';

          var visualization = vistk.viz()
            .params({
              type: 'dotplot',
              width: 800,
              height: 100,
              margin: {top: 10, right: 10, bottom: 30, left: 30},
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_group: '%s',
              var_x: '%s',
              var_y: function() { return this.height/2; },
              var_text: '%s',
              var_color: '%s',
              items: [{
                attr: "name",
                marks: [{
                  type: "diamond",
                  fill: function(d, i, vars) { return d[vars.var_color]; }
                }, {
                  var_mark: '__highlighted',
                  type: d3.scale.ordinal().domain([true, false]).range(["text", "none"]),
                  translate: [0, -20]
                }]
              }],
              time: {
                var_time: 'year',
                current_time: %s,
                parse: function(d) { return d; }
              }
            });

        d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.group, self.x, self.name, self.color, self.year)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Sparkline(VisTkViz):

    def __init__(self, x="year", y="y", id="id", color="color", group=None, name=None, year=2013):
        super(Sparkline, self).__init__()
        self.id = id
        self.x = x
        self.y = y
        self.year = year
        self.color = color
        self.group = group

        if name is None:
            self.name = id
        else:
            self.name = name

    def draw_viz(self, json_data):

        js = """
        (function (){

          var viz_data = %s;
          var viz_container = '#%s';

          var visualization = vistk.viz()
            .params({
              type: 'sparkline',
              width: 800,
              height: 100,
              margin: {top: 10, right: 10, bottom: 30, left: 30},
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_group: '%s',
              var_x: 'year',
              var_y: '%s',
              var_text: '%s',
              var_color: '%s',
              items: [{
                attr: "name",
                marks: [{
                  type: "diamond",
                  width: 10,
                  height: 10
                }, {
                  var_mark: '__highlighted',
                  type: d3.scale.ordinal().domain([true, false]).range(["text", "none"]),
                  translate: [0, -20]
                }]
              }],
              time: {
                var_time: 'year',
                current_time: %s,
                parse: function(d) { return d; }
              }
            });

        d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.group, self.y, self.name, self.color, self.year)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Geomap(VisTkViz):

    WORLD_JSON = open(os.path.join(path, "../sourcedata/geomap/world-110m.json")).read()
    # WORLD_NAME = open(os.path.join(path, "../sourcedata/geomap/world-country-names.tsv")).read()

    WORLD_NAME = []
    with open(os.path.join(path, "../sourcedata/geomap/world-country-names.tsv")) as f:
        f_tsv = csv.reader(f, delimiter='\t')
        for row in f_tsv:
          a = {}
          a[row[0]] = row[1]
          WORLD_NAME.append(a)

    def __init__(self, id="id", color="color", name=None, year=2013):
        super(Geomap, self).__init__()
        self.id = id
        self.year = year
        self.color = color

        if name is None:
            self.name = id
        else:
            self.name = name

    def draw_viz(self, json_data):

        js = """
        (function (){

          var viz_data = %s;
          var world = %s;
          var names = %s;
          var viz_container = '#%s';

          console.log("NAMES", names)
        //  queue()
        //      .defer(d3.json, "../geomap/world-110m.json")
        //      .defer(d3.tsv, "../geomap/world-country-names.tsv")
        //      .await(ready);

        //  function ready(error, world, names) {

            var visualization = vistk.viz()
              .params({
                dev: true,
                type: 'geomap',
                width: 800,
                height: 600,
                margin: {top: 10, right: 10, bottom: 30, left: 30},
                topology: world,
                names: names,
                container: viz_container,
                data: viz_data,
                var_id: '%s',
                var_group: 'continent',
                var_x: 'x',
                var_y: 'y',
                var_text: '%s',
                var_color: '%s',
                items: [{
                  attr: "name",
                  marks: [{
                    type: "shape",
                    fill: d3.scale.linear().domain([0, 1]).range(["red", "green"])
                  }]
                }],
                time: {
                  var_time: 'year',
                  current_time: %s,
                  parse: function(d) { return d; }
                }
              });

            d3.select(viz_container).call(visualization);

        //  }

        })();
        """ % (json_data, self.WORLD_JSON, self.WORLD_NAME, self.container_id, self.id, self.name, self.color, self.year)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Linechart(VisTkViz):

    def __init__(self, x="year", y="y", id="id", name=None, color=None, group=None):
        super(Linechart, self).__init__()
        self.id = id
        self.x = x
        self.y = y
        self.group = group

        if name is None:
            self.name = id
        else:
            self.name = name

        if color is None:
            self.color = id
        else:
            self.color = color

    def draw_viz(self, json_data):

        js = """
        (function (){

          var viz_data = %s;
          var viz_container = '#%s';
          console.log("DATA", viz_data)
          var visualization = vistk.viz()
            .params({
              type: 'linechart',
              width: 800,
              height: 600,
              margin: {top: 10, right: 10, bottom: 30, left: 30},
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_group: '%s',
              var_color: '%s',
              var_x: '%s',
              var_y: '%s',
              var_text: '%s',
              y_invert: true,
              color: d3.scale.ordinal().domain(["Africa", "Americas", "Asia", "Europe", "Oceania"]).range(["#99237d", "#c72439", "#6bc145", "#88c7ed", "#dd9f98"]),
              time: {
                parse: d3.time.format('%%Y').parse,
                var_time: 'year',
                current_time: vistk.utils.max
              },
            });

          d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.group, self.color, self.x, self.y, self.name)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))
