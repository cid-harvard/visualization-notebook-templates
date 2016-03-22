from IPython.core.display import display_html, display, HTML, Javascript
import json
import random
import pandas as pd
import csv

import os
path = os.path.dirname(__file__)

__radius_min = 5
__radius_max = 10
__opacity = 1

class VisTkViz(object):

    JS_LIBS = ['https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js',
               'http://cid-harvard.github.io/vis-toolkit/js/topojson.js',
               'http://cid-harvard.github.io/vis-toolkit/build/vistk.js']

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
        self.legend_id = self.create_container()
        data = self.preprocess_data(data)
        json_data = self.handle_data(data)
        self.draw_viz(json_data)

    def draw_viz(self, json_data):
        raise NotImplementedError()

    def update(self):

        js = """
        (function (visualization){
          visualization.params().var_sort_asc = !visualization.params().var_sort_asc;
          visualization.params().init = true
          visualization.params().refresh = true
          d3.select(visualization.container()).call(visualization);
        })(window.visualization)
        """

        display(Javascript(lib=self.JS_LIBS, data=js))

class Treemap(VisTkViz):

    def __init__(self, id='id', group='group', name=None, color=None, size=None, year=1995, filter=None, sort=None, title=''):
        super(Treemap, self).__init__()

        self.id = id
        self.group = group
        self.year = year
        self.sort = sort
        self.title = title

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
        window.visualization = null;
        (function (visualization){

          var viz_data = %s;
          var viz_container = '#%s';

          visualization = vistk.viz()
                .params({
                  type: 'treemap',
                  container: viz_container,
                  height: 600,
                  width: 900,
                  margin: {top: 20, right: 10, bottom: 10, left: 10},
                  data: viz_data,
                  var_id: '%s',
                  var_sort: '%s',
                  var_group: '%s',
                  var_color: '%s',
                  var_size: '%s',
                  var_text: '%s',
                  items: [{
                    marks: [{
                   //   type: "text",
                   //   filter: function(d) { return d.depth == 1 && d.dx > 30 && d.dy > 30; },
                   //   translate: [5, 0]
                   // }, {
                      type: "rect",
                      filter: function(d, i) { return d.depth == 2; },
                      x: 0,
                      y: 0,
                      width: function(d) { return d.dx; },
                      height: function(d) { return d.dy; },
                      fill: function(d, i, vars) { return d[vars.var_color]; }
                    }, {
                      var_mark: '__highlighted',
                      type: d3.scale.ordinal().domain([true, false]).range(['text', 'none']),
                      translate: [10, 10]
                    }]
                  }],
                  time: {
                    var_time: 'year',
                    current_time: %s
                  },
                  title: '%s'
                });

            d3.select(viz_container).call(visualization);
        })(window.visualization);
        """ % (json_data, self.container_id, self.id, self.sort, self.group, self.color, self.size,
               self.name, self.year, self.title)

        html_src = """
          <link href='https://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class TreemapColor(VisTkViz):

    def __init__(self, id='id', group='group', name=None, color=None, size=None, year=1995, filter=None, sort=None, title='',  color_range=['red', 'green'], color_domain=[0, 1]):
        super(TreemapColor, self).__init__()

        self.id = id
        self.group = group
        self.year = year
        self.sort = sort
        self.title = title
        self.color_range = color_range
        self.color_domain = color_domain

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
        window.visualization = null;
        (function (visualization){

          var viz_data = %s;
          var viz_container = '#%s';

          visualization = vistk.viz()
                .params({
                  type: 'treemap',
                  container: viz_container,
                  height: 600,
                  width: 900,
                  margin: {top: 20, right: 10, bottom: 10, left: 10},
                  data: viz_data,
                  var_id: '%s',
                  var_sort: '%s',
                  var_group: '%s',
                  var_color: '%s',
                  color: d3.scale.linear().domain(%s).range(%s),
                  var_size: '%s',
                  var_text: '%s',
                  items: [{
                    marks: [{
                      type: "text",
                      filter: function(d) { return d.depth === 1 && d.dx > 30 && d.dy > 30; },
                      translate: [5, 0]
                    }, {
                      type: "rect",
                      filter: function(d, i) { return d.depth == 2; },
                      x: 0,
                      y: 0,
                      width: function(d) { return d.dx; },
                      height: function(d) { return d.dy; }
                    }, {
                      var_mark: '__highlighted',
                      filter: function(d) { return d.depth === 2; },
                      type: d3.scale.ordinal().domain([true, false]).range(['text', 'none']),
                      translate: [10, 10]
                    }]
                  }],
                  time: {
                    var_time: 'year',
                    current_time: %s
                  },
                  title: '%s'
                });

            d3.select(viz_container).call(visualization);
        })(window.visualization);
        """ % (json_data, self.container_id, self.id, self.sort, self.group, self.color, self.color_domain, self.color_range, self.size,
               self.name, self.year, self.title)

        html_src = """
          <link href='https://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Scatterplot(VisTkViz):

    def __init__(self, x="x", y="y", id="id", r="r", name=None, color=None, group=None, year=2013):
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

        if group is None:
            self.group = id
        else:
            self.group = group

        if color is None:
            self.color = id
        else:
            self.color = color

    def draw_viz(self, json_data):

        js = """
        (function (){

          var viz_data = %s;
          var viz_container = '#%s';

          var params = {
                type: 'scatterplot',
                width: 800,
                height: 600,
                margin: {top: 10, right: 10, bottom: 30, left: 30},
                container: viz_container,
                data: viz_data,
                var_id: '%s',
                var_group: '%s',
                color: function(d) { return d; },
                var_color: '%s',
                radius_min: %s,
                radius_max: %s,
                var_x: '%s',
                var_y: '%s',
                var_r: '%s',
                var_text: '%s',
                items: [{
                  marks: [{
                    type: 'circle'
                  }, {
                    var_mark: '__selected',
                    type: d3.scale.ordinal().domain([true, false]).range(["text", "none"]),
                    translate: [10, 10]
                  }, {
                    var_mark: '__highlighted',
                    type: d3.scale.ordinal().domain([true, false]).range(["text", "none"]),
                    translate: [10, 10]
                  }]
                }],
                time: {
                  var_time: 'year',
                  current_time: %s,
                  parse: function(d) { return d; }
                }
              };

          params.connect = [{
            marks: [{
              var_mark: '__highlighted',
              type: d3.scale.ordinal().domain([true, false]).range(['path', 'none']),
              stroke: function(d, i, vars) {
                return vars.color(vars.accessor_data(d)[vars.var_color]);
              },
              stroke_width: 2,
              fill: function(d) {
                return 'none';
              },
              func: function(d, i, vars) {

                return d3.svg.line()
                   .interpolate(vars.interpolate)
                   .x(function(d) {
                     return vars.x_scale[0]['func'](d[vars.var_x]);
                   })
                   .y(function(d) {
                     return vars.y_scale[0]['func'](d[vars.var_y]);
                   })(d);
                 }
            }]
          }];

          var visualization = vistk.viz()
            .params(params);

          d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.group, self.color, 5, 10, self.x, self.y, self.r, self.name, self.year)

        html_src = """
          <link href='https://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class PieScatterplot(VisTkViz):

    def __init__(self, x="x", y="y", id="id", r="r", name=None, color=None, group=None, year=2013, var_time='year', share=None, title=''):
        super(PieScatterplot, self).__init__()
        self.id = id
        self.x = x
        self.y = y
        self.r = r
        self.year = year
        self.var_time = var_time
        self.title = title

        if name is None:
            self.name = id
        else:
            self.name = name

        if group is None:
            self.group = id
        else:
            self.group = group

        if color is None:
            self.color = id
        else:
            self.color = color

        if share is None:
            self.share = self.r
        else:
            self.share = share

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
              var_group: '%s',
              color: d3.scale.ordinal().domain(["Africa", "Americas", "Asia", "Europe", "Oceania"]).range(["#99237d", "#c72439", "#6bc145", "#88c7ed", "#dd9f98"]),
              var_color: 'cutoff',
              radius_min: %s,
              radius_max: %s,
              var_x: '%s',
              var_y: '%s',
              var_r: '%s',
              var_text: '%s',
              var_share: '%s',
              items: [{
                marks: [{
                  var_mark: '__aggregated',
                  type: d3.scale.ordinal().domain([true, false]).range(["circle", "none"]),
                  fill: "white"
                }, {
                  var_mark: '__aggregated',
                  type: d3.scale.ordinal().domain([true, false]).range(["piechart", "none"]),
                  var_share: 'nb_products',
                  class: 'piechart'
                }, {
                  var_mark: '__aggregated',
                  type: d3.scale.ordinal().domain([true, false]).range(["text", "none"])
                }]
              }],
              set: {
                __aggregated: true
              },
              time: {
                var_time: '%s',
                current_time: %s,
                parse: function(d) { return d; }
              },
              title: '%s'
            });

        d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.group, 5, 10, self.x, self.y, self.r, self.name, self.share, self.var_time, self.year, self.title)

        html_src = """
          <link href='https://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Caterplot(VisTkViz):

    def __init__(self, x="x", y="y", id="id", r="r", name=None, color=None, group=None, year=2013, selection=[]):
        super(Caterplot, self).__init__()
        self.id = id
        self.x = x
        self.y = y
        self.r = r
        self.year = year
        self.selection = selection

        if name is None:
            self.name = id
        else:
            self.name = name

        if group is None:
            self.group = id
        else:
            self.group = group

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
              type: 'caterplot',
              width: 800,
              height: 600,
              margin: {top: 30, right: 30, bottom: 30, left: 30},
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_group: '%s',
              var_color: '%s',
              radius_min: 5,
              radius_max: 20,
              var_x: '%s',
              var_y: '%s',
              var_r: '%s',
              var_text: 'name',
              time: {
                var_time: 'year',
                current_time: %s
              },
              selection: %s
            });

        d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.group, self.color, self.x, self.y, self.r, self.year, self.selection)

        html_src = """
          <link href='https://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class CaterplotTime(VisTkViz):

    def __init__(self, x="x", y="y", id="id", r="r", name=None, color=None, group=None, year=2013, selection=[]):
        super(CaterplotTime, self).__init__()
        self.id = id
        self.x = x
        self.y = y
        self.r = r
        self.year = year
        self.selection = selection

        if name is None:
            self.name = id
        else:
            self.name = name

        if group is None:
            self.group = id
        else:
            self.group = group

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
              type: 'caterplot_time',
              width: 800,
              height: 600,
              margin: {top: 30, right: 30, bottom: 30, left: 30},
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_group: '%s',
              var_color: '%s',
              radius_min: 10,
              radius_max: 30,
              var_x: '%s',
              var_y: '%s',
              var_r: '%s',
              var_text: 'name',
              time: {
                var_time: 'year',
                current_time: %s
              },
              selection: %s
            });

        d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.group, self.color, self.x, self.y, self.r, self.year, self.selection)

        html_src = """
          <link href='https://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Dotplot(VisTkViz):

    def __init__(self, x="x", id="id", color="color", name=None, group=None, year=2013, selection=[], x_domain=[], title=''):
        super(Dotplot, self).__init__()
        self.id = id
        self.x = x
        self.year = year
        self.color = color
        self.selection = selection
        self.x_domain = x_domain
        self.title = title

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
              margin: {top: 10, right: 100, bottom: 30, left: 30},
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_group: '%s',
              var_x: '%s',
              x_domain: %s,
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
                }, {
                  var_mark: '__selected',
                  type: d3.scale.ordinal().domain([true, false]).range(["text", "none"]),
                  translate: [0, -20]
                }]
              }],
              time: {
                var_time: 'year',
                current_time: %s,
                parse: function(d) { return d; }
              },
              selection: %s,
              title: '%s'
            });

        d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.group, self.x, self.x_domain, self.name, self.color,
          self.year, self.selection, self.title)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Sparkline(VisTkViz):

    def __init__(self, x="year", y="y", mark="diamond", id="id", color="color", group=None, name=None, year=2013):
        super(Sparkline, self).__init__()
        self.id = id
        self.x = x
        self.y = y
        self.mark = mark
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
              margin: {top: 10, right: 100, bottom: 30, left: 30},
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_group: '%s',
              var_x: '%s',
              var_y: '%s',
              var_text: '%s',
              var_color: '%s',
              items: [{
                marks: [{
                  type: '%s',
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
        """ % (json_data, self.container_id, self.id, self.group, self.x, self.y, self.name, self.color, self.mark, self.year)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Geomap(VisTkViz):

    WORLD_JSON = open(os.path.join(path, "../sourcedata/geomap/world-110m.json")).read()

    WORLD_NAME = []
    # https://raw.githubusercontent.com/cid-harvard/vis-toolkit-datasets/gh-pages/data/world-country-names.tsv
    with open(os.path.join(path, "../sourcedata/geomap/world-country-names.tsv")) as f:
        f_tsv = csv.reader(f, delimiter='\t')
        for row in f_tsv:
          WORLD_NAME.append({'id': row[0], 'name': row[1]})

    def __init__(self, id="id", color="color", group='continent', name=None, year=2013, color_range=["red", "green"], title=''):
        super(Geomap, self).__init__()
        self.id = id
        self.year = year
        self.color = color
        self.color_range = color_range
        self.title = title
        self.group = group

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

          var var_color = '%s';
          var color_domain = vistk.utils.extent(viz_data, var_color);

          var color_scale = d3.scale.linear().domain(color_domain).range(%s);

          var visualization = vistk.viz()
            .params({
              dev: true,
              type: 'geomap',
              width: 700,
              height: 400,
              margin: {top: 10, right: 10, bottom: 30, left: 30},
              topology: world,
              names: names,
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_names: '%s',
              var_group: '%s',
              var_x: 'x',
              var_y: 'y',
              var_text: '%s',
              var_color: var_color,
              items: [{
                marks: [{
                  type: "shape",
                  fill: function(d, i, vars) {

                    if(typeof d === 'undefined' || d.data.__no_data) {
                      return 'lightgray';
                    } else {
                      return color_scale(d.data[vars.var_color]);
                    }
                  }
                }],
              }],
              time: {
                var_time: 'year',
                current_time: %s,
                parse: function(d) { return d; }
              },
              title: '%s'
            })

          d3.select(viz_container).call(visualization);

          var width = 500;
          var format = d3.format(".2s");
          var viz_legend = '#%s';

          var colors = d3.range(5).map(function(d, i) {
            return (d + 1) * (color_domain[1] - color_domain[0])/5;
          });

          var legend = vistk.viz()
                .params({
                  dev: true,
                  height: 60,
                  width: 700,
                  margin: {top: 0, right: 100, bottom: 0, left: 50},
                  type: 'ordinal_horizontal',
                  data: colors,
                  container: viz_legend,
                  var_text: '__value',
                  var_color: '__value',
                  var_group: '__value',
                  var_x: '__id',
                  var_y: '__id',
                  x_ticks: 10,
                  items: [{
                    marks: [{
                      type: "rect",
                      rotate: "0",
                      width: width/colors.length,
                      height: 20,
                      fill: function(d) {
                        if(typeof d === 'undefined') {
                          return 'lightgray';
                        } else {
                          return color_scale(d.__value);
                        }
                      }
                    }, {
                      type: "text",
                      translate: [width/colors.length/2, 25],
                      text_anchor: 'middle',
                      text: function(d, i) {
                        return format(d['__value']).replace('G', 'B');
                      }
                    }]
                  }]
                });

            d3.select(viz_legend).call(legend);

        })();
        """ % (json_data, self.WORLD_JSON, self.WORLD_NAME, self.container_id,
          self.color, self.color_range, self.id, self.id, self.group, self.name, self.year, self.title,
          self.legend_id)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Linechart(VisTkViz):

    def __init__(self, x="year", y="y", id="id", y_invert=True, name=None, color=None, group=None, selection=[]):
        super(Linechart, self).__init__()
        self.id = id
        self.x = x
        self.y = y
        self.group = group
        self.selection = selection

        if name is None:
            self.name = id
        else:
            self.name = name

        if color is None:
            self.color = id
        else:
            self.color = color

        if y_invert is True:
            self.y_invert = 'true'
        else:
            self.y_invert = 'false'

    def draw_viz(self, json_data):

        js = """
        (function (){

          var viz_data = %s;
          var viz_container = '#%s';

          var visualization = vistk.viz()
            .params({
              type: 'linechart',
              width: 800,
              height: 600,
              margin: {top: 30, right: 100, bottom: 30, left: 30},
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_group: '%s',
              var_color: '%s',
              var_x: '%s',
              var_y: '%s',
              var_text: '%s',
              y_invert: %s,
              marks: [{
                type: 'circle',
                fill: function(d, i, vars) { return d['color']; }
              }, {
                var_mark: '__highlighted',
                type: d3.scale.ordinal().domain([true, false]).range(['text', 'none']),
                translate: [10, 0],
                text: function(d, i, vars) {
                  return vars.accessor;
                }
              }],
              color: d3.scale.ordinal().domain(["Africa", "Americas", "Asia", "Europe", "Oceania"]).range(["#99237d", "#c72439", "#6bc145", "#88c7ed", "#dd9f98"]),
              time: {
                parse: function(d) { return d; },
                var_time: 'year',
                current_time: vistk.utils.max
              },
              selection: %s,
            });

          d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.group, self.color, self.x, self.y, self.name, self.y_invert, self.selection)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Grid(VisTkViz):

    def __init__(self, id="id", color="color", name=None, group=None, sort=None, r=None, year=2013):
        super(Grid, self).__init__()
        self.id = id
        self.year = year
        self.color = color
        self.sort = sort
        self.r = r

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
              type: 'grid',
              width: 800,
              height: 600,
              margin: {top: 10, right: 10, bottom: 30, left: 30},
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_group: '%s',
              var_sort: '%s',
              var_text: '%s',
              var_color: '%s',
              var_sort_asc: true,
              var_r: '%s',
              items: [{
                attr: "name",
                marks: [{
                  type: "circle"
                }, {
                  var_mark: '__highlighted',
                  type: d3.scale.ordinal().domain([true, false]).range(['text', 'none']),
                  translate: [10, 0]
                }, {
                  var_mark: '__selected',
                  type: d3.scale.ordinal().domain([true, false]).range(['text', 'none']),
                  translate: [10, 0]
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
        """ % (json_data, self.container_id, self.id, self.group, self.sort, self.name, self.color, self.r, self.year)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Productspace(VisTkViz):

    GRAPH_DATA = open(os.path.join(path, "../classifications/atlas_international_product_space_hs4_codes.json")).read()

    def __init__(self, x="x", y="y", id="id", r="r", name=None, color=None, group=None, year=2013):
        super(Productspace, self).__init__()
        self.id = id
        self.x = x
        self.y = y
        self.r = r
        self.year = year

        if name is None:
            self.name = id
        else:
            self.name = name

        if group is None:
            self.group = id
        else:
            self.group = group

        if color is None:
            self.color = id
        else:
            self.color = color

    def draw_viz(self, json_data):

        js = """
        (function (){

          var graph = %s;

          // graph.nodes.forEach(function(node) {
          //   node.id = node.id.slice(2,6);
          // });

          var viz_data = %s;
          var viz_container = '#%s';

          var visualization = vistk.viz()
            .params({
              type: 'productspace',
              width: 800,
              height: 600,
              margin: {top: 10, right: 10, bottom: 30, left: 30},
              container: viz_container,
              nodes: graph.nodes,
              links: graph.edges,
              data: viz_data,
              var_id: '%s',
              var_group: 'continent',
              var_color: '%s',
              var_x: 'x',
              var_y: 'y',
              x_axis_show: false,
              x_grid_show: false,
              y_axis_show: false,
              y_grid_show: false,
              y_invert: true,
              radius: 5,
              var_group: 'community_name',
              var_text: 'name',
              items: [{
                marks: [{
                  type: "circle",
                  fill: function(d) {
                    if(d.rca > 1) {
                      return d.color;
                    } else {
                      return "#fff";
                    }
                  }
                }, {
                  var_mark: '__highlighted',
                  type: d3.scale.ordinal().domain([true, false]).range(['text', 'none']),
                  translate: [10, 0]
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
        """ % (self.GRAPH_DATA, json_data, self.container_id, self.id, self.color, self.year)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

class Stackedgraph(VisTkViz):

    def __init__(self, x="year", y="y", id="id", name=None, color=None, group=None, selection=[], year=2013):
        super(Stackedgraph, self).__init__()
        self.id = id
        self.x = x
        self.y = y
        self.group = group
        self.selection = selection
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
              type: 'stacked',
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
              y_invert: false,
              time: {
                parse: function(d) { return d3.time.format("%%Y").parse(d+""); },
                var_time: 'year',
                current_time: %s
              },
              selection: %s,
            });

          d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.group, self.color, self.x, self.y, self.name, self.year, self.selection)

        html_src = """
          <link href='http://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))
