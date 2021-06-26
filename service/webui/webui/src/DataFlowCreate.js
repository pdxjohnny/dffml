import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import React, { useState } from 'react';
import ReactFlow, { Controls, updateEdge, addEdge } from 'react-flow-renderer';

import mermaid from 'mermaid';
import MD5 from "crypto-js/md5";

import TestDataFlow from './DataFlowCreateTestDataFlowAutomatingClassification';

const onLoad = (reactFlowInstance) => reactFlowInstance.fitView();

const styles = theme => ({
  paper: {
    maxWidth: 936,
    margin: 'auto',
    overflow: 'hidden',
  },
  searchBar: {
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
  },
  searchInput: {
    fontSize: theme.typography.fontSize,
  },
  block: {
    display: 'block',
  },
  addUser: {
    marginRight: theme.spacing(1),
  },
  contentWrapper: {
    margin: '40px 16px',
  },
});

// Take a dataflow. Return mermaid diagram syntax for that dataflow.
async function dataflowToDiagram(dataflow) {
  // TODO implement. Use dffml/cli/dataflow.py as a base. Ideally we can write
  // in one language, compile to wasm, and only maintain one implementation
  return `
graph TD
subgraph a759a07029077edc5c37fea0326fa281[Processing Stage]
style a759a07029077edc5c37fea0326fa281 fill:#afd388b5,stroke:#a4ca7a
f577c71443f6b04596b3fe0511326c40[check_if_valid_git_repository_URL]
155b8fdb5524f6bfd5adbae4940ad8d5[clone_git_repo]
70c47962ba601f0df1890f4c72ae1b54[count_authors]
90b953c5527ed3a579912eea8b02b1be[git_commits]
0afa2b3dbc72afa67170525d1d7532d7[git_repo_author_lines_for_dates]
7bbb97768b34f207c34c1f4721708675[git_repo_commit_from_date]
546062a96122df465d2631f31df4e9e3[git_repo_default_branch]
7f20bd2c94ecbd47ab6bd88673c7174f[make_quarters]
9dc9f9feff38d8f5dd9388d3a60e74c0[quarters_back_to_date]
67e92c8765a9bc7fb2d335c459de9eb5[work]
end
subgraph a4827add25f5c7d5895c5728b74e2beb[Cleanup Stage]
style a4827add25f5c7d5895c5728b74e2beb fill:#afd388b5,stroke:#a4ca7a
e74c0c8fc6f55c309253f7be9b1dd288[cleanup_git_repo]
end
subgraph 58ca4d24d2767176f196436c2890b926[Output Stage]
style 58ca4d24d2767176f196436c2890b926 fill:#afd388b5,stroke:#a4ca7a
defec9eabb5f189af6e09162fe2361f0[group_by]
end
subgraph inputs[Inputs]
style inputs fill:#f6dbf9,stroke:#a178ca
7ec43cbbf66e6d893180645d5e929bb4(seed<br>URL)
7ec43cbbf66e6d893180645d5e929bb4 --> f577c71443f6b04596b3fe0511326c40
155b8fdb5524f6bfd5adbae4940ad8d5 --> e74c0c8fc6f55c309253f7be9b1dd288
7ec43cbbf66e6d893180645d5e929bb4(seed<br>URL)
7ec43cbbf66e6d893180645d5e929bb4 --> 155b8fdb5524f6bfd5adbae4940ad8d5
f577c71443f6b04596b3fe0511326c40 --> 155b8fdb5524f6bfd5adbae4940ad8d5
0afa2b3dbc72afa67170525d1d7532d7 --> 70c47962ba601f0df1890f4c72ae1b54
546062a96122df465d2631f31df4e9e3 --> 90b953c5527ed3a579912eea8b02b1be
155b8fdb5524f6bfd5adbae4940ad8d5 --> 90b953c5527ed3a579912eea8b02b1be
9dc9f9feff38d8f5dd9388d3a60e74c0 --> 90b953c5527ed3a579912eea8b02b1be
546062a96122df465d2631f31df4e9e3 --> 0afa2b3dbc72afa67170525d1d7532d7
155b8fdb5524f6bfd5adbae4940ad8d5 --> 0afa2b3dbc72afa67170525d1d7532d7
9dc9f9feff38d8f5dd9388d3a60e74c0 --> 0afa2b3dbc72afa67170525d1d7532d7
546062a96122df465d2631f31df4e9e3 --> 7bbb97768b34f207c34c1f4721708675
9dc9f9feff38d8f5dd9388d3a60e74c0 --> 7bbb97768b34f207c34c1f4721708675
155b8fdb5524f6bfd5adbae4940ad8d5 --> 7bbb97768b34f207c34c1f4721708675
155b8fdb5524f6bfd5adbae4940ad8d5 --> 546062a96122df465d2631f31df4e9e3
cccf733931f477734312ad8b7389c4b1(seed<br>group_by_spec)
cccf733931f477734312ad8b7389c4b1 --> defec9eabb5f189af6e09162fe2361f0
a8b3d979c7c66aeb3b753408c3da0976(seed<br>quarters)
a8b3d979c7c66aeb3b753408c3da0976 --> 7f20bd2c94ecbd47ab6bd88673c7174f
3261e0991aae6690cf0359a79dee8aaf(seed<br>quarter_start_date)
3261e0991aae6690cf0359a79dee8aaf --> 9dc9f9feff38d8f5dd9388d3a60e74c0
7f20bd2c94ecbd47ab6bd88673c7174f --> 9dc9f9feff38d8f5dd9388d3a60e74c0
0afa2b3dbc72afa67170525d1d7532d7 --> 67e92c8765a9bc7fb2d335c459de9eb5
end`;
}

// Take a dataflow diagarm. Return the parsed XML DOM of the mermaid
// SVG of the diagram.
function diagramToSVG(diagram) {
  return new Promise((resolve, reject) => {
    mermaid.mermaidAPI.render('graphDiv', diagram, function(svgCode, bindFunctions) {
      resolve((new DOMParser()).parseFromString(svgCode, "image/svg+xml"));
    });
  });
}

async function dataflowToElements(dataflow) {
  let elements = [];

  // Example elements from react flow tutorial
  const example = [
    {
      id: '1',
      type: 'input',
      data: { label: 'Node A' },
      position: { x: 250, y: 0 },
    },
    {
      id: '2',
      data: { label: 'Node B' },
      position: { x: 100, y: 200 },
    },
    { id: 'e1-2', source: '1', target: '2', label: 'updatable edge' },
  ];

  // TODO Make some more generic interface so we aren't tied to mermaid.
  // Main concern here is how to map nodes to elements and back across
  // diagramming libraries will probably result in different CSS selectors
  // needed.
  // We don't have to worry about this if
  // https://github.com/wbkd/react-flow/issues/1194 is fixed. We're only using
  // mermaid to get the correct X, Y, for each element.
  const diagram = await dataflowToDiagram(dataflow);
  const svg = await diagramToSVG(diagram);
  const svg_nodes = svg.querySelectorAll(".node,.default");

  let operation_instance_name_md5_to_svg_node = {};
  for (let i = 0; i < svg_nodes.length; i++) {
    let node = svg_nodes[i];
    let node_md5 = node.id.split("-")[1];
    operation_instance_name_md5_to_svg_node[node_md5] = node;
  }

  Object.keys(dataflow.flow).forEach(function(operation_instance_name, id) {
    let flow = dataflow.flow[operation_instance_name];

    let node_md5 = MD5(operation_instance_name).toString();
    let svg_node = operation_instance_name_md5_to_svg_node[node_md5];

    // transform="translate(599.1979103088379,219.66666984558105)"
    let transform = svg_node.attributes.transform.nodeValue;

    // The node
    // Example:
    // {
    //   id: '3',
    //   data: { label: 'Node C' },
    //   position: { x: 400, y: 200 },
    // },
    elements[operation_instance_name] = {
      id: operation_instance_name,
      data: { label: operation_instance_name },
      position: {
        x: 2 * Number(transform.substring(transform.indexOf("(") + 1, transform.indexOf(","))),
        y: 2 * Number(transform.substring(transform.indexOf(",") + 1, transform.indexOf(")"))),
      },
    };

    // The inputs
    // Example:
    // { id: 'e1-2', source: '1', target: '2', label: 'updatable edge' },
    Object.keys(flow.inputs).forEach(function(input_name) {
      // {
      //     "conditions": [
      //         "seed"
      //     ],
      //     "inputs": {
      //         "repo": [
      //             {
      //                 "clone_git_repo": "repo"
      //             }
      //         ]
      //     }
      // }
      flow.inputs[input_name].forEach(function(origin) {
        let source = undefined;

        // Three types of origins to support
        if (typeof origin === "string") {
          // Single string origin ("seed")
          source = origin;
          // Add an element for the origin if it doesn't exist
          if (!elements.hasOwnProperty(source)) {
            // TODO How to calculate x, y?
          }
        } else if (typeof origin === "object") {
          // Output of another operation
          // source = Object.keys(origin)[0] + ".outputs." + origin[Object.keys(origin)[0]];
          source = Object.keys(origin)[0];
        } else if (false) {
          // TODO Accept alternate definitions from list
        }

        elements[operation_instance_name + ".inputs." + input_name] = {
          id: operation_instance_name + ".inputs." + input_name,
          source: source,
          target: operation_instance_name,
          label: input_name,
        };
      });
    });
  });

  console.log(elements)

  return Object.values(elements);
}

async function elementsToDataFlow(elements, dataflow) {
  // TODO Take modified elements and the old dataflow. Return the dataflow
  // updated to reflect any changes to elements.
  return dataflow;
}

function DataFlow(props) {
  const { elements, modifyElements } = props;

  // Called after end of edge gets dragged to another source or target
  const onEdgeUpdate = (oldEdge, newConnection) =>
    modifyElements("onEdgeUpdate", {oldEdge: oldEdge, newConnection: newConnection}, (els) => updateEdge(oldEdge, newConnection, els));
  const onConnect = (params) => modifyElements("onConnect", {params: params}, (els) => addEdge(params, els));

  // TODO Call elementsModified on updates to the flow

  return (
    <ReactFlow
      elements={elements}
      onLoad={onLoad}
      snapToGrid
      onEdgeUpdate={onEdgeUpdate}
      onConnect={onConnect}
    >
      <Controls />
    </ReactFlow>
  );
}

DataFlow.propTypes = {
  classes: PropTypes.object.isRequired,
  elements: PropTypes.array.isRequired,
  modifyElements: PropTypes.func.isRequired,
};

function DataFlowLoader(props) {
  const { modifyDataFlow } = props;

  return (
    <p>TODO</p>
  );
}

DataFlowLoader.propTypes = {
  classes: PropTypes.object.isRequired,
  modifyDataFlow: PropTypes.func.isRequired,
};

function Content(props) {
  const { classes, backend } = props;
  const [ dataflow, setDataFlow ] = useState({});
  const [ elements, setElements ] = useState([]);

  async function modifyDataFlow(dataflow) {
    console.log("modifyDataFlow", dataflow);
    setDataFlow(dataflow);
    setElements(await dataflowToElements(dataflow));
  }

  async function modifyElements(event, data, elements) {
    console.log("modifyElements", event, data, elements);
    setElements(elements);
    setDataFlow(await elementsToDataFlow(elements, dataflow));
  }

  // TODO Replace this with upload or create mechanism
  if (Object.keys(dataflow).length === 0) {
    modifyDataFlow(TestDataFlow);
  }

  return (
    <React.Fragment>
      <DataFlowLoader
        classes={classes}
        modifyDataFlow={modifyDataFlow}
      />
      <DataFlow
        classes={classes}
        elements={elements}
        modifyElements={modifyElements}
      />
    </React.Fragment>
  );
}

Content.propTypes = {
  classes: PropTypes.object.isRequired,
  backend: PropTypes.object.isRequired,
};

export default withStyles(styles)(Content);
