from typing import Dict, List, Any,Callable
from ..df.types import Definition,Dataflow
from ..df.base import op



def mediator(dataflow,mapping_data,extra_defintions=[]):
    """

            {
                "mapping_name" :
                    {
                        'input_types' : [("results",flow_results")]
                        "redirect_function" : some callable
                        "output_types" : [("name":"flow_outputs")]
                        "kwargs" : {}

                    }

            }

    """
    df_definitions=dataflow.definitions
    df_definitions.extend(extra_definitions)
    df_ops = dataflow.operations
    df_op_imps = dataflow.implementations

    created_ops = []
    created_op_imps = []
    for mapping_name,contents in mapping_data.items():
        # build inputs for the op
        op_inputs = { val[0]:val[1] for val in contents['input_types']}
        op_outputs = { val[0]:val[1] for val in contents['output_types']}
        temp_op = op(
                    name=mapping_name,
                    inputs=op_inputs,
                    outputs=op_outputs,
                    **contents["kwargs"]
                    )(contents['redirect_function'])
        created_ops.append(temp_op)
        created_op_imps.append(temp_op.op)

    df_ops.extend(created_ops)
    df_op_imps.extend(created_op_imps)

    new_dataflow = DataFlow(
        operations = df_ops,
        seed = dataflow.seed
        configs = dataflow.configs,
        definitions=df_definitions,
        implementations = df_op_imps
    )
    return new_dataflow
