from typing import Dict, List, Any,Callable
from dffml.df.types import Definition,DataFlow
from dffml.df.base import op



def add_ops_to_dataflow(dataflow,mapping_data,extra_definitions={}):
    """
        creates and adds operations to `dataflow` to connect operations differing
        in output -> input definitions,or to reformat output of one operation as
        input of other.

        eg:- `mapping_data`
            {
                "mapping_name" :
                    {
                        'input_types' : [("results","flow_results")]
                        "redirect_function" : lambda x : {"input for some other op":results}
                        "output_types" : [("input for some other op":"definition name of the same")]
                        "kwargs" : {}

                    }

            }

        Another use case would be to insert/update db with an intemediate operation which
        publishes data from some flow output.

    """
    df_definitions = dataflow.definitions
    extra_definitions.update(df_definitions)
    df_ops = dataflow.operations
    df_op_imps = dataflow.implementations

    for mapping_name,contents in mapping_data.items():
        # build inputs,outputs for the connecting operation
        op_inputs = { val[0]:extra_definitions[val[1]] for val in contents['input_types']}
        op_outputs = { val[0]:extra_definitions[val[1]] for val in contents['output_types']}
        temp_op = op(
                    name=mapping_name,
                    inputs=op_inputs,
                    outputs=op_outputs,
                    **contents.get("kwargs",{})
                    )(contents['redirect_function'])

        df_ops[mapping_name]=temp_op
        df_op_imps[mapping_name]=temp_op.imp

    new_dataflow = DataFlow(
        operations = df_ops,
        seed = dataflow.seed,
        configs = dataflow.configs,
        implementations = df_op_imps
    )
    return new_dataflow
