from IPython.core.display import display, HTML, Javascript
import json
import random
import pandas as pd

import os
path = os.path.dirname(__file__)

class D3PlusViz(object):

    JS_LIBS = ['http://www.d3plus.org/js/d3.js',
               'http://www.d3plus.org/js/d3plus.js']

    def create_container(self):
        container_id = "d3plus_div_{id}".format(id=random.randint(0, 100000))
        container = """<div id='{id}' style='height:600px;'></div>"""\
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


class Treemap(D3PlusViz):

    def __init__(self, id=['group', 'id'], name=None, color=None):
        super(Treemap, self).__init__()
        self.id = id
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

          debugger;

          var viz_data = %s;

          var visualization = d3plus.viz()
          .legend(false)
          .container("#%s")
          .type("tree_map")
          .size({
            'value': "value",
            'threshold': false
          })
          .id(%s)
          .color(%s)
          .text(%s)
          .depth(1)
          .data(viz_data)
          .draw();

        })();
        """ % (json_data, self.container_id, self.id, self.color, self.name)

        display(Javascript(lib=self.JS_LIBS, data=js))


class Scatterplot(D3PlusViz):

    def __init__(self, x="x", y="y", id="id", name=None, color=None):
        super(Scatterplot, self).__init__()
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

          var visualization = d3plus.viz()
          .legend(false)
          .container("#%s")
          .data(viz_data)
          .type("scatter")
          .id("%s")
          .color("%s")
          .text("%s")
          .x("%s")
          .y("%s")
          .depth(1)
          .size("value")
          .draw();

        })();
        """ % (json_data, self.container_id, self.id, self.color,
               self.name, self.x, self.y)

        display(Javascript(lib=self.JS_LIBS, data=js))



class ProductSpace(D3PlusViz):

    GRAPH_DATA = open(os.path.join(path, "../classifications/atlas_international_product_space_hs4_codes.json")).read()

    def __init__(self, id='id', name=None, color=None, size=10):
        super(ProductSpace, self).__init__()
        self.id = id
        if name is None:
            self.name = id
        else:
            self.name = name
        if color is None:
            self.color = id
        else:
            self.color = color
        self.size = size

    def preprocess_data(self, data):
        return data.rename(columns={self.id: "id"})

    def draw_viz(self, json_data):

        js = """
        (function (){

          debugger;

          var viz_data = %s;
          var graph_data = %s;

          var visualization = d3plus.viz()
          .legend(false)
          .labels(false)
          .container("#%s")
          .type("network")
          .nodes(graph_data.nodes)
          .edges(graph_data.edges)
          .size("%s")
          .active({
            "value": function(d){
              return d.M == 1;
            },
            "spotlight":true
          })
          .id('%s')
          .color('%s')
          .text('%s')
          .data(viz_data)
          .draw();

        })();
        """ % (json_data, self.GRAPH_DATA, self.container_id, self.size, "id", self.color, self.name)

        display(Javascript(lib=self.JS_LIBS, data=js))


class SITCProductSpace(ProductSpace):
    GRAPH_DATA = open(os.path.join(path, "../classifications/atlas_international_product_space_sitc_codes.json")).read()
