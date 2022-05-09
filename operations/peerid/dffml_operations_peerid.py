"""
.. code-block:: console

    $ pip install peerdid

"""
# SPDX-License-Identifier: Apache-2.0
# Source: https://github.com/sicpa-dlab/peer-did-python/blob/c63461860891d7c111abb6b24a51f23dad845a74/tests/test_vectors.py#L58-L95
# All of these become Inputs within top level context when pointed at DID, it
# should introspect and map to operation config (service -> orchestrator /
# service to talk to for data).
_EXAMPLE_PEER_DID_DOC = {
    "id": "did:peer:2.Ez6LSbysY2xFMRpGMhb7tFTLMpeuPRaqaWM1yECx2AtzE3KCc.Vz6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V.Vz6MkgoLTnTypo3tDRwCkZXSccTPHRLhF4ZnjhueYAFpEX6vg.SeyJ0IjoiZG0iLCJzIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9lbmRwb2ludCIsInIiOlsiZGlkOmV4YW1wbGU6c29tZW1lZGlhdG9yI3NvbWVrZXkiXSwiYSI6WyJkaWRjb21tL3YyIiwiZGlkY29tbS9haXAyO2Vudj1yZmM1ODciXX0",
    "authentication": [
       {
           "id": "did:peer:2.Ez6LSbysY2xFMRpGMhb7tFTLMpeuPRaqaWM1yECx2AtzE3KCc.Vz6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V.Vz6MkgoLTnTypo3tDRwCkZXSccTPHRLhF4ZnjhueYAFpEX6vg.SeyJ0IjoiZG0iLCJzIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9lbmRwb2ludCIsInIiOlsiZGlkOmV4YW1wbGU6c29tZW1lZGlhdG9yI3NvbWVrZXkiXSwiYSI6WyJkaWRjb21tL3YyIiwiZGlkY29tbS9haXAyO2Vudj1yZmM1ODciXX0#6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V",
           "type": "Ed25519VerificationKey2018",
           "controller": "did:peer:2.Ez6LSbysY2xFMRpGMhb7tFTLMpeuPRaqaWM1yECx2AtzE3KCc.Vz6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V.Vz6MkgoLTnTypo3tDRwCkZXSccTPHRLhF4ZnjhueYAFpEX6vg.SeyJ0IjoiZG0iLCJzIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9lbmRwb2ludCIsInIiOlsiZGlkOmV4YW1wbGU6c29tZW1lZGlhdG9yI3NvbWVrZXkiXSwiYSI6WyJkaWRjb21tL3YyIiwiZGlkY29tbS9haXAyO2Vudj1yZmM1ODciXX0",
           "publicKeyBase58": "ByHnpUCFb1vAfh9CFZ8ZkmUZguURW8nSw889hy6rD8L7"
       },
       {
           "id": "did:peer:2.Ez6LSbysY2xFMRpGMhb7tFTLMpeuPRaqaWM1yECx2AtzE3KCc.Vz6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V.Vz6MkgoLTnTypo3tDRwCkZXSccTPHRLhF4ZnjhueYAFpEX6vg.SeyJ0IjoiZG0iLCJzIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9lbmRwb2ludCIsInIiOlsiZGlkOmV4YW1wbGU6c29tZW1lZGlhdG9yI3NvbWVrZXkiXSwiYSI6WyJkaWRjb21tL3YyIiwiZGlkY29tbS9haXAyO2Vudj1yZmM1ODciXX0#6MkgoLTnTypo3tDRwCkZXSccTPHRLhF4ZnjhueYAFpEX6vg",
           "type": "Ed25519VerificationKey2018",
           "controller": "did:peer:2.Ez6LSbysY2xFMRpGMhb7tFTLMpeuPRaqaWM1yECx2AtzE3KCc.Vz6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V.Vz6MkgoLTnTypo3tDRwCkZXSccTPHRLhF4ZnjhueYAFpEX6vg.SeyJ0IjoiZG0iLCJzIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9lbmRwb2ludCIsInIiOlsiZGlkOmV4YW1wbGU6c29tZW1lZGlhdG9yI3NvbWVrZXkiXSwiYSI6WyJkaWRjb21tL3YyIiwiZGlkY29tbS9haXAyO2Vudj1yZmM1ODciXX0",
           "publicKeyBase58": "3M5RCDjPTWPkKSN3sxUmmMqHbmRPegYP1tjcKyrDbt9J"
       }
    ],
    "keyAgreement": [
       {
           "id": "did:peer:2.Ez6LSbysY2xFMRpGMhb7tFTLMpeuPRaqaWM1yECx2AtzE3KCc.Vz6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V.Vz6MkgoLTnTypo3tDRwCkZXSccTPHRLhF4ZnjhueYAFpEX6vg.SeyJ0IjoiZG0iLCJzIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9lbmRwb2ludCIsInIiOlsiZGlkOmV4YW1wbGU6c29tZW1lZGlhdG9yI3NvbWVrZXkiXSwiYSI6WyJkaWRjb21tL3YyIiwiZGlkY29tbS9haXAyO2Vudj1yZmM1ODciXX0#6LSbysY2xFMRpGMhb7tFTLMpeuPRaqaWM1yECx2AtzE3KCc",
           "type": "X25519KeyAgreementKey2019",
           "controller": "did:peer:2.Ez6LSbysY2xFMRpGMhb7tFTLMpeuPRaqaWM1yECx2AtzE3KCc.Vz6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V.Vz6MkgoLTnTypo3tDRwCkZXSccTPHRLhF4ZnjhueYAFpEX6vg.SeyJ0IjoiZG0iLCJzIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9lbmRwb2ludCIsInIiOlsiZGlkOmV4YW1wbGU6c29tZW1lZGlhdG9yI3NvbWVrZXkiXSwiYSI6WyJkaWRjb21tL3YyIiwiZGlkY29tbS9haXAyO2Vudj1yZmM1ODciXX0",
           "publicKeyBase58": "JhNWeSVLMYccCk7iopQW4guaSJTojqpMEELgSLhKwRr"
       }
    ],
    "service": [
       {
           "id": "did:peer:2.Ez6LSbysY2xFMRpGMhb7tFTLMpeuPRaqaWM1yECx2AtzE3KCc.Vz6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V.Vz6MkgoLTnTypo3tDRwCkZXSccTPHRLhF4ZnjhueYAFpEX6vg.SeyJ0IjoiZG0iLCJzIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9lbmRwb2ludCIsInIiOlsiZGlkOmV4YW1wbGU6c29tZW1lZGlhdG9yI3NvbWVrZXkiXSwiYSI6WyJkaWRjb21tL3YyIiwiZGlkY29tbS9haXAyO2Vudj1yZmM1ODciXX0#didcommmessaging-0",
           "type": "DIDCommMessaging",
           "serviceEndpoint": "https://example.com/endpoint",
           "routingKeys": [
               "did:example:somemediator#somekey"
           ],
           "accept": [
                "didcomm/v2", "didcomm/aip2;env=rfc587"
           ]
       }
    ]
}

# Shim:
#   - Validate schema
#     - Then call this if the format is DID


async def dataflow_from_peer_did(self):
    pass

# SPDX-License-Identifier: Apache-2.0
# Source: https://github.com/sicpa-dlab/peer-did-python/blob/c63461860891d7c111abb6b24a51f23dad845a74/demo/demo.py
from peerdid.did_doc import DIDDocPeerDID
from peerdid.peer_did import (
    create_peer_did_numalgo_0,
    create_peer_did_numalgo_2,
    resolve_peer_did,
)
from peerdid.types import (
    VerificationMaterialAuthentication,
    VerificationMaterialAgreement,
    VerificationMethodTypeAgreement,
    VerificationMethodTypeAuthentication,
    VerificationMaterialFormatPeerDID,
)


import pathlib
import contextlib

CACHED_DOWNLOADS = pathlib.Path(__file__).parent.joinpath(".tools", "downloads")


# FireFly Linux download
# TODO Expand to use generic download from github repo flow (see recording for
# details)
# - Check content length
# - Trigger operation to request disk quota
# - Receive content body once content length confirmed available within quota /
#   system local resource management, i.e. traverse `Input` parents and
#   interact with backing scarce resource.
CACHED_FIREFLY_CLI = (
    "https://github.com/hyperledger/firefly-cli/releases/download/v1.0.1/firefly-cli_1.0.1_Linux_x86_64.tar.gz",
    "38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6e1da274edebfe76f65fbd51ad2f14898b95b",
)


@dffml.config
class FireFlyConfig:
    download_url: str dffml.field("URL to FireFly CLI", default=CACHED_FIREFLY_CLI[0])
    download_hash: str dffml.field("SHA384 hash for FireFly CLI", default=CACHED_FIREFLY_CLI[1])
    cache_dir: str dffml.field("Directory to stored cached download of FireFly CLI", default=CACHED_DOWNLOADS)


# Imp enter could be run dataflow which either connects to remote firefly or
# downloads and runs (ssh tunnels, proxies, etc.)
# TODO Remove context manager when we fix op imp_enter and ctx_enter to not
# attempt context entry before setting return value on parent key given if
# return value is not a context manager. We want to call coroutines instead of
# entering their context.
@contextlib.asynccontextmanager
async def download_firefly_cli(self, url, hash_value, cache_dir):
    # TODO For generic case we should remove any query string found after last
    # suffix (?..., #...)
    firefly_cli = await cached_download_unpack_archive(
        url,
        cache_dir.joinpath("firefly-cli." + '.'.join(pathlib.Path(url).suffixes)),
        cache_dir.joinpath("firefly-cli-download"),
        hash_value,
    )
    return firefly_cli

@dffml.op(
    imp_enter={
        "firefly": lambda self: download_firefly_cli(self, self.config),
    }
)
async def firefly_import(self):
    """
    Takes inputs
    """

    return
    encryption_keys = [
        VerificationMaterialAgreement(
            type=VerificationMethodTypeAgreement.X25519_KEY_AGREEMENT_KEY_2019,
            format=VerificationMaterialFormatPeerDID.BASE58,
            value="DmgBSHMqaZiYqwNMEJJuxWzsGGC8jUYADrfSdBrC6L8s",
        )
    ]
    signing_keys = [
        VerificationMaterialAuthentication(
            type=VerificationMethodTypeAuthentication.ED25519_VERIFICATION_KEY_2018,
            format=VerificationMaterialFormatPeerDID.BASE58,
            value="ByHnpUCFb1vAfh9CFZ8ZkmUZguURW8nSw889hy6rD8L7",
        )
    ]
    service = """
                {
                    "type": "DIDCommMessaging",
                    "serviceEndpoint": "https://example.com/endpoint1",
                    "routingKeys": ["did:example:somemediator#somekey1"],
                    "accept": ["didcomm/v2", "didcomm/aip2;env=rfc587"]
                }
            """

    peer_did_algo_0 = create_peer_did_numalgo_0(inception_key=signing_keys[0])
    peer_did_algo_2 = create_peer_did_numalgo_2(
        encryption_keys=encryption_keys, signing_keys=signing_keys, service=service
    )

    print("peer_did_algo_0:" + peer_did_algo_0)
    print("==================================")
    print("peer_did_algo_2:" + peer_did_algo_2)
    print("==================================")

    did_doc_algo_0_json = resolve_peer_did(peer_did=peer_did_algo_0)
    did_doc_algo_2_json = resolve_peer_did(peer_did=peer_did_algo_2)
    print("did_doc_algo_0 as JSON:" + did_doc_algo_0_json)
    print("==================================")
    print("did_doc_algo_2 as JSON:" + did_doc_algo_2_json)

    did_doc_algo_0 = DIDDocPeerDID.from_json(did_doc_algo_0_json)
    did_doc_algo_2 = DIDDocPeerDID.from_json(did_doc_algo_2_json)
    print("did_doc_algo_0 as object:" + str(did_doc_algo_0.to_dict()))
    print("==================================")
    print("did_doc_algo_2 as object:" + str(did_doc_algo_2.to_dict()))


# From DFFML
from typing import Dict, Any

from ..base import config
from ..df.base import op, OperationImplementationContext
from ..df.types import DataFlow, Input, Definition


class InvalidCustomODAPContext(Exception):
    """
    Thrown when custom inputs for dffml.dataflow.run do not list an input with
    string as its primitive as the first input.
    """


class InvalidCustomODAPOutputs(Exception):
    """
    Thrown when outputs for a custom dffml.dataflow.run do not match that of
    it's subflow.
    """


@config
class ODAPConfig:
    dataflow: DataFlow


DEFAULT_INPUTS = {
    "inputs": Definition(name="flow_inputs", primitive="Dict[str,Any]")
}


@op(
    name="dffml.dataflow.run",
    inputs=DEFAULT_INPUTS,
    outputs={
        "results": Definition(name="flow_results", primitive="Dict[str,Any]")
    },
    config_cls=ODAPConfig,
    expand=["results"],
)
class run_dataflow(OperationImplementationContext):
    """
    Starts a subflow ``self.config.dataflow`` and adds ``inputs`` in it.

    Parameters
    ----------
    inputs : dict
        The inputs to add to the subflow. These should be a key value mapping of
        the context string to the inputs which should be seeded for that context
        string.

    Returns
    -------
    dict
        Maps context strings in inputs to output after running through dataflow.

    Examples
    --------

    The following shows how to use run dataflow in its default behavior.

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> URL = Definition(name="URL", primitive="string")
    >>>
    >>> subflow = DataFlow.auto(GetSingle)
    >>> subflow.definitions[URL.name] = URL
    >>> subflow.seed.append(
    ...     Input(
    ...         value=[URL.name],
    ...         definition=GetSingle.op.inputs["spec"]
    ...     )
    ... )
    >>>
    >>> dataflow = DataFlow.auto(run_dataflow, GetSingle)
    >>> dataflow.configs[run_dataflow.op.name] = ODAPConfig(subflow)
    >>> dataflow.seed.append(
    ...     Input(
    ...         value=[run_dataflow.op.outputs["results"].name],
    ...         definition=GetSingle.op.inputs["spec"]
    ...     )
    ... )
    >>>
    >>> async def main():
    ...     async for ctx, results in MemoryOrchestrator.run(dataflow, {
    ...         "run_subflow": [
    ...             Input(
    ...                 value={
    ...                     "dffml": [
    ...                         {
    ...                             "value": "https://github.com/intel/dffml",
    ...                             "definition": URL.name
    ...                         }
    ...                     ]
    ...                 },
    ...                 definition=run_dataflow.op.inputs["inputs"]
    ...             )
    ...         ]
    ...     }):
    ...         print(results)
    >>>
    >>> asyncio.run(main())
    {'flow_results': {'dffml': {'URL': 'https://github.com/intel/dffml'}}}

    The following shows how to use run dataflow with custom inputs and outputs.
    This allows you to run a subflow as if it were an operation.

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> URL = Definition(name="URL", primitive="string")
    >>>
    >>> @op(
    ...     inputs={"url": URL},
    ...     outputs={"last": Definition("last_element_in_path", primitive="string")},
    ... )
    ... def last_path(url):
    ...     return {"last": url.split("/")[-1]}
    >>>
    >>> subflow = DataFlow.auto(last_path, GetSingle)
    >>> subflow.seed.append(
    ...     Input(
    ...         value=[last_path.op.outputs["last"].name],
    ...         definition=GetSingle.op.inputs["spec"],
    ...     )
    ... )
    >>>
    >>> dataflow = DataFlow.auto(run_dataflow, GetSingle)
    >>> dataflow.operations[run_dataflow.op.name] = run_dataflow.op._replace(
    ...     inputs={"URL": URL},
    ...     outputs={last_path.op.outputs["last"].name: last_path.op.outputs["last"]},
    ...     expand=[],
    ... )
    >>> dataflow.configs[run_dataflow.op.name] = ODAPConfig(subflow)
    >>> dataflow.seed.append(
    ...     Input(
    ...         value=[last_path.op.outputs["last"].name],
    ...         definition=GetSingle.op.inputs["spec"],
    ...     )
    ... )
    >>> dataflow.update(auto_flow=True)
    >>>
    >>> async def main():
    ...     async for ctx, results in MemoryOrchestrator.run(
    ...         dataflow,
    ...         {
    ...             "run_subflow": [
    ...                 Input(value="https://github.com/intel/dffml", definition=URL)
    ...             ]
    ...         },
    ...     ):
    ...         print(results)
    >>>
    >>> asyncio.run(main())
    {'last_element_in_path': 'dffml'}
    """

    async def run_default(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        The default implementation for the dataflow.run operation is the uctx
        mode. This mode is when we map unique strings to a list of inputs to be
        given to the respective string's context.
        """
        inputs_created = {}
        definitions = self.config.dataflow.definitions

        for ctx_str, val_defs in inputs.items():
            inputs_created[ctx_str] = [
                Input(
                    value=val_def["value"],
                    definition=definitions[val_def["definition"]],
                )
                for val_def in val_defs
            ]
        async with self.subflow(self.config.dataflow) as octx:
            results = [
                {(await ctx.handle()).as_string(): result}
                async for ctx, result in octx.run(inputs_created)
            ]

        return {"results": results}

    async def run_custom(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # TODO Move string primitive validation into init of
        # an OperationImplementation (and then keep this as the context).
        ctx_input_name, ctx_definition = list(self.parent.op.inputs.items())[0]

        if ctx_definition.primitive != "string":
            raise InvalidCustomODAPContext(ctx_definition.export())

        subflow_inputs = {inputs[ctx_input_name]: []}

        for input_name, value in inputs.items():
            definition = self.parent.op.inputs[input_name]
            subflow_inputs[inputs[ctx_input_name]].append(
                Input(value=value, definition=definition)
            )

        op_outputs = sorted(self.parent.op.outputs.keys())

        async with self.subflow(self.config.dataflow) as octx:
            async for ctx, result in octx.run(subflow_inputs):
                if op_outputs != sorted(result.keys()):
                    raise InvalidCustomODAPOutputs(
                        ctx_definition.export()
                    )
                return result

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Support redefinition of operation
        if self.parent.op.inputs == DEFAULT_INPUTS:
            return await self.run_default(inputs["inputs"])
        else:
            return await self.run_custom(inputs)
