import os
import json

from .base import Operation, \
                  BaseParameterSet, \
                  BaseInputNetworkContext, \
                  BaseLockNetworkContext

from .memory import MemoryOperationImplementationNetwork, \
                    MemoryOperationImplementationNetworkContext

HTML = '''<!DOCTYPE html>
<html>
<head>
  <title>Data Flow Network</title>

  <meta charset="UTF-8">

  <script type="text/javascript" src="http://visjs.org/dist/vis.js"
    integrity="sha384-+vn6nehU2NqyZcvnLAhSjRq+o1uUPqJFpUjlcPv9hAwFhpdMvfceYn3KDEM7UyQr"
    crossorigin="anonymous"></script>

  <link href="http://visjs.org/dist/vis-network.min.css" rel="stylesheet" type="text/css"
    integrity="sha384-hv6STAGuk4qTwmryFbZZTn3QrGRyZW1soC9K/Dy68zs8subBFOU69tg/GGZfkIBb"
    crossorigin="anonymous" />

  <style type="text/css">
    html, body, div {
      width: 100%;
      height: 100%;
    }
  </style>
</head>
<body>

<div id="mynetwork"></div>

<script type="text/javascript">
var old_inputs = "";
var old_connections = "";

async function loadit() {
  var inputs = await (await fetch('inputs.json')).json();
  if (old_inputs === JSON.stringify(inputs)) {
    console.log(old_inputs, JSON.stringify(inputs));
    return;
  } else {
    old_inputs = JSON.stringify(inputs);
  }
  // create an array with nodes
  var nodes = new vis.DataSet(inputs);

  var connections = await (await fetch('connections.json')).json();
  if (old_connections === JSON.stringify(connections)) {
    console.log(old_connections, JSON.stringify(connections));
    return;
  } else {
    old_connections = JSON.stringify(connections);
  }

  // create an array with edges
  var edges = new vis.DataSet(connections);

  // create a network
  var container = document.getElementById('mynetwork');
  var data = {
    nodes: nodes,
    edges: edges
  };
  var options = {
    layout: {
      randomSeed: 2,
      hierarchical: {
        levelSeparation: 335,
        nodeSpacing: 335,
        direction: "UD",
        sortMethod: "directed"
      }
    },
    interaction: {dragNodes :true},
    physics: {
      enabled: false
    },
  };
  var network = new vis.Network(container, data, options);
}

loadit();
</script>
</body>
</html>
'''

class GraphingMemoryOperationImplementationNetworkContext(MemoryOperationImplementationNetworkContext):

    async def run_dispatch(self,
            ictx: BaseInputNetworkContext,
            lctx: BaseLockNetworkContext,
            operation: Operation,
            parameter_set: BaseParameterSet):
        '''
        Write out operation and inputs and outputs to be viewed as a graph
        '''
        if not operation.name in self.map_to_id:
            self.map_to_id[operation.name] = self.id
            self.inputs.append({
                'id': self.id,
                'label': operation.name,
                'color': 'lightgreen'
                })
            self.id += 1
        async for parameter in parameter_set.parameters():
            if not parameter.origin.uid in self.map_to_id:
                self.map_to_id[parameter.origin.uid] = self.id
                self.inputs.append({
                    'id': self.id,
                    'label': str(parameter.origin),
                    'color': 'lightblue'
                    })
                self.id += 1
            else:
                for i in range(0, len(self.inputs)):
                    if self.inputs[i]['id'] == \
                            self.map_to_id[parameter.origin.uid]:
                        self.inputs[i]['color'] = 'lightblue'
            self.connections.append({
                'from': self.map_to_id[parameter.origin.uid],
                'to': self.map_to_id[operation.name],
                'arrows': 'to'
                })
        inputs = await super().run_dispatch(ictx, lctx, operation,
                                            parameter_set)
        for item in inputs:
            if not item.uid in self.map_to_id:
                self.map_to_id[item.uid] = self.id
                self.inputs.append({
                    'id': self.id,
                    'label': '%s: %s' % (item.definition.name, \
                        str(item.value)[:15] + (str(item.value)[15:] and '..')),
                    'color': 'orange'
                    })
                self.id += 1
            self.connections.append({
                'from': self.map_to_id[operation.name],
                'to': self.map_to_id[item.uid],
                'arrows': 'to'
                })

    async def __aenter__(self) -> 'GraphingMemoryOperationImplementationNetworkContext':
        self.id = 0
        self.map_to_id = {}
        self.inputs = []
        self.connections = []
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if not os.path.isdir('html'):
            os.mkdir('html', mode=0o700)
        with open(os.path.join('html', 'index.html'), 'w') as handle:
            handle.write(HTML)
        with open(os.path.join('html', 'inputs.json'), 'w') as handle:
            json.dump(self.inputs, handle)
        with open(os.path.join('html', 'connections.json'), 'w') as handle:
            json.dump(self.connections, handle)

class GraphingMemoryOperationImplementationNetwork(MemoryOperationImplementationNetwork):

    def __call__(self) -> GraphingMemoryOperationImplementationNetworkContext:
        return GraphingMemoryOperationImplementationNetworkContext(self)
