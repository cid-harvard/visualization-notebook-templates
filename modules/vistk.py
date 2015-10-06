from IPython.core.display import display_html, display, HTML, Javascript
import json
import random
import pandas as pd

import os
path = os.path.dirname(__file__)

class VisTkViz(object):

    JS_LIBS = ['https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js',
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
        data = self.preprocess_data(data)
        json_data = self.handle_data(data)
        self.draw_viz(json_data)

    def draw_viz(self, json_data):
        raise NotImplementedError()


class Treemap(VisTkViz):

    def __init__(self, id='id', group='group', name=None, color=None, size=None, year=1995, filter=None):
        super(Treemap, self).__init__()

        self.id = id
        self.group = group
        self.year = year

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
                  var_sort: 'nb_products',
                  var_group: '%s',
                  var_color: '%s',
                  title: 'Countries',
                  var_size: '%s',
                  var_text: '%s',
                  time: {
                    var_time: 'year',
                    current_time: %s
                  }
                });

            d3.select(viz_container).call(visualization);
        })();
        """ % (json_data, self.container_id, self.id, self.group, self.color, self.size,
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

    def __init__(self, x="x", id="id", color="color", name=None, year=2013):
        super(Dotplot, self).__init__()
        self.id = id
        self.x = x
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
              var_group: 'continent',
              var_x: '%s',
              var_y: function() { return this.height/2; },
              var_text: '%s',
              var_color: '%s',
              items: [{
                attr: "name",
                marks: [{
                  type: "diamond",
                  rotate: "0"
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
        """ % (json_data, self.container_id, self.id, self.x, self.name, self.color, self.year)

        display(Javascript(lib=self.JS_LIBS, data=js))

class Linechart(VisTkViz):

    def __init__(self, x="x", y="y", id="id", name=None, color=None):
        super(Linechart, self).__init__()
        self.id = id
        self.x = x
        self.y = y

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
              margin: {top: 10, right: 10, bottom: 30, left: 30},
              container: viz_container,
              data: viz_data,
              var_id: '%s',
              var_group: 'continent',
              var_color: '%s',
              var_x: '%s',
              var_y: '%s',
              var_r: '%s',
              var_text: 'name'
              type: 'linechart',
              container: viz_container,
              margin: {top: 30, right: 100, bottom: 30, left: 10},
              data: viz_data,
              var_id: '%s',
              var_color: '%s',
              color: d3.scale.ordinal().domain(["Africa", "Americas", "Asia", "Europe", "Oceania"]).range(["#99237d", "#c72439", "#6bc145", "#88c7ed", "#dd9f98"]),
              var_text: 'name',
              y_text: 'ECI Rank',
              var_x: '%s',
              var_y: '%s',
              time: {
                parse: d3.time.format('\%Y').parse,
                var_time: 'year',
                current_time: '2013'
              },
            });

        d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.color, self.x, self.y)

        display(Javascript(lib=self.JS_LIBS, data=js))
