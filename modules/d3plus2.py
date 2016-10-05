from IPython.core.display import display, HTML, Javascript
import json
import random
import pandas as pd

import pprint

import os
path = os.path.dirname(__file__)


def rgb2hexcolor(r, g, b):
    """Convert 3 integer r, g, b values into hexadecimal #ff00ac format color."""
    return '#' + ''.join('{:02x}'.format(a) for a in [int(r), int(g), int(b)])


class RawJavascript(str):
    """Placeholder class that's the same as a string BUT is treated specially
    by format_js_value and not quoted."""
    pass


def format_js_value(thing):
    if type(thing) == str:
        return "'{}'".format(thing)
    if type(thing) == bool:
        return "{}".format(thing).lower()
    if type(thing) == int:
        return "{}".format(thing)
    if type(thing) == int:
        return "{}".format(thing)
    if type(thing) == list:
        return (
            "[" +
            ",".join(format_js_value(x) for x in thing) +
            "]"
        )
    if type(thing) == dict:
        return (
            "{" +
            ",".join(
                format_js_value(k) + ": " + format_js_value(v)
                for k, v in thing.items()
            ) +
            "}"
        )
    elif type(thing) == RawJavascript:
        return str(thing)
    else:
        raise ValueError("""Object you passed in must either be a string or
                         Javascript() object.""")


class D3PlusViz(object):

    JS_LIBS = ['http://www.d3plus.org/js/d3.js',
               'http://www.d3plus.org/js/d3plus.js']

    def generate_container_id(self):
        return "d3plus_div_{id}".format(id=random.randint(0, 100000))

    def create_container(self):
        container_id = self.generate_container_id()
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
        """Draw a visualization in an ipython notebook."""
        self.container_id = self.create_container()
        data = self.preprocess_data(data)
        json_data = self.handle_data(data)
        display(self.generate_js(json_data))

    def dump_html(self, data, container_id=None):
        """Dump a single-file self-contained html string designed to be loaded
        up into the browser on its own or embedded in a page."""
        data = self.preprocess_data(data)
        json_data = self.handle_data(data)

        html_template = """
        <div id='{container_id}'></div>
        {scripts}
        <script>
        {code}
        </script>
        """
        script_template = "<script src='{src}' type='text/javascript'></script>"

        if container_id is None:
            self.container_id = self.generate_container_id()

        code = self.generate_js(json_data).data
        scripts = "".join([script_template.format(src=x) for x in self.JS_LIBS])

        return html_template.format(container_id=self.container_id, scripts=scripts, code=code)

    def generate_js(self, json_data):
        raise NotImplementedError()


class Treemap(D3PlusViz):

    def __init__(self, id=['group', 'id'], value="value", name=None, color=None, tooltip=[]):
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
        self.value = value
        self.tooltip=tooltip

    def generate_js(self, json_data):

        js = """
        (function (){{

          debugger;

          var viz_data = {viz_data};

          var visualization = d3plus.viz()
          .legend(false)
          .container({container})
          .type("tree_map")
          .size({{
            'value': {value},
            'threshold': false
          }})
          .id({id})
          .color({color})
          .text({text})
          .tooltip({tooltip})
          .depth(1)
          .data(viz_data)
          .draw();

        }})();
        """.format(
            viz_data=json_data,
            container=format_js_value("#" + self.container_id),
            id=format_js_value(self.id),
            value=format_js_value(self.value),
            color=format_js_value(self.color),
            text=format_js_value(self.name),
            tooltip=format_js_value(self.tooltip)
        )

        return Javascript(lib=self.JS_LIBS, data=js)


class Scatterplot(D3PlusViz):

    def __init__(self, x="x", y="y", id="id", name=None, color=None, size=10, tooltip=[]):
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
        self.size=size
        self.tooltip=tooltip

    def generate_js(self, json_data):

        js = """
        (function (){{

          var viz_data = {viz_data};

          var visualization = d3plus.viz()
          .legend(false)
          .container({container})
          .data(viz_data)
          .type("scatter")
          .id({id})
          .color({color})
          .text({text})
          .tooltip({tooltip})
          .x({x})
          .y({y})
          .depth(1)
          .size({size})
          .draw();

        }})();
        """.format(
            viz_data=json_data,
            container=format_js_value("#" + self.container_id),
            id=format_js_value(self.id),
            size=format_js_value(self.size),
            color=format_js_value(self.color),
            text=format_js_value(self.name),
            x=format_js_value(self.x),
            y=format_js_value(self.y),
            tooltip=format_js_value(self.tooltip)
        )

        return Javascript(lib=self.JS_LIBS, data=js)



class ProductSpace(D3PlusViz):

    HS_GRAPH_DATA = open(os.path.join(path, "../classifications/atlas_international_product_space_hs4_codes.json")).read()
    SITC_GRAPH_DATA = open(os.path.join(path, "../classifications/atlas_international_product_space_sitc_codes.json")).read()

    def __init__(self, id='id', name=None, color=None, size=10,
                 graph_data=None, presence="M", spotlight=True,
                 tooltip=[], node_property="nodes", edge_property="edges", network_id="id"):
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
        if graph_data is None:
            self.graph_data = self.HS_GRAPH_DATA
        else:
            self.graph_data = graph_data
        self.size = size
        self.presence = presence
        self.spotlight = spotlight
        self.tooltip = tooltip
        self.node_property = node_property
        self.edge_property = edge_property
        self.network_id = network_id

    def preprocess_data(self, data):
        return data.rename_axis({self.id: self.network_id}, axis=1)

    def network_help(self):
        net_obj = json.loads(self.graph_data)
        nodes = net_obj[self.node_property]
        edges = net_obj[self.edge_property]

        print("ID key: ", self.id)
        print("Network ID key: ", self.network_id)

        print("Node example: \n", pprint.pformat(nodes[0]))
        print("Edge example: \n", pprint.pformat(edges[0]))

        print("Node values: \n", [x[self.id] for x in nodes])

    def generate_js(self, json_data):

        js = """
        (function (){{

          debugger;

          var viz_data = {viz_data};
          var graph_data = {graph_data};

          var visualization = d3plus.viz()
          .legend(false)
          .labels(false)
          .container({container})
          .type("network")
          .nodes(graph_data.{node_property})
          .edges(graph_data.{edge_property})
          .size({size})
          .active({{
            "value": function(d){{
              return d.{presence} == 1;
            }},
            "spotlight":{spotlight}
          }})
          .id({id})
          .color({color})
          .text({text})
          .tooltip({tooltip})
          .data(viz_data)
          .draw();

        }})();
        """.format(viz_data=format_js_value(RawJavascript(json_data)),
                   graph_data=format_js_value(RawJavascript(self.graph_data)),
                   container=format_js_value('#' + self.container_id),
                   size=format_js_value(self.size),
                   id=format_js_value(self.network_id),
                   presence=format_js_value(RawJavascript(self.presence)),
                   spotlight=format_js_value(self.spotlight),
                   color=format_js_value(self.color),
                   text=format_js_value(self.name),
                   tooltip=format_js_value(self.tooltip),
                   node_property=format_js_value(RawJavascript(self.node_property)),
                   edge_property=format_js_value(RawJavascript(self.edge_property))
                   )

        return Javascript(lib=self.JS_LIBS, data=js)
