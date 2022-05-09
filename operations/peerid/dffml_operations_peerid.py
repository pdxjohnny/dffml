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


import os
import pathlib
import contextlib

import dffml

from typing import Dict, Any


CACHED_DOWNLOADS = pathlib.Path(__file__).parent.joinpath(".tools", "downloads")


# SSIService Linux download
# TODO Expand to use generic download from github repo flow (see recording for
# details)
# - Check content length
# - Trigger operation to request disk quota
# - Receive content body once content length confirmed available within quota /
#   system local resource management, i.e. traverse `Input` parents and
#   interact with backing scarce resource.
CACHED_SSI_SERVICE_CLI = (
    "https://github.com/TBD54566975/ssi-service/archive/bb54e46c306ba7fc20e5a1af85f2ea9454f78a86.tar.gz",
    "324442ba5d854ae7668a211795e90f5eb216420777d51965fb9773929b602660953169c80f0ac161b714420d594f3513",
)


@dffml.config
class SSIServiceConfig:
    download_url: str = dffml.field("URL to SSIService CLI", default=CACHED_SSI_SERVICE_CLI[0])
    download_hash: str = dffml.field("SHA384 hash for SSIService CLI", default=CACHED_SSI_SERVICE_CLI[1])
    cache_dir: str = dffml.field("Directory to stored cached download of SSIService CLI", default=CACHED_DOWNLOADS)


# Imp enter could be run dataflow which either connects to remote ssi_service or
# downloads and runs (ssh tunnels, proxies, etc.)
# TODO Remove context manager when we fix op imp_enter and ctx_enter to not
# attempt context entry before setting return value on parent key given if
# return value is not a context manager. We want to call coroutines instead of
# entering their context.
@contextlib.asynccontextmanager
async def download_ssi_service(self, url, hash_value, cache_dir):
    # TODO Implement load from file(s) on start if given (another pathlib.Path
    # argument after cache_dir)
    # TODO For generic case we should remove any query string found after last
    # suffix (?..., #...)

    # Golang for mage
    golang_url = "https://go.dev/dl/go1.18.1.linux-amd64.tar.gz"
    golang_sha = ""
    golang = await dffml.cached_download_unpack_archive(
        golang_url,
        cache_dir.joinpath("golang." + ''.join(pathlib.Path(golang_url).suffixes)),
        cache_dir.joinpath("golang-download"),
        golang_sha,
    )

    # Mage requires go
    mage_url = "https://github.com/magefile/mage/releases/download/v1.13.0/mage_1.13.0_Linux-64bit.tar.gz"
    mage_sha = "b4adb5b8e2239fbcd04367df5c6f4a3fa4b6a8bc7ffb2c79b300850a669dcd786606ea3af2b6014beffd257d9cbbc218"
    mage = await dffml.cached_download_unpack_archive(
        mage_url,
        cache_dir.joinpath("mage." + ''.join(pathlib.Path(mage_url).suffixes)),
        cache_dir.joinpath("mage-download"),
        mage_sha,
    )
    # SSI Service is packaged as docker but we must build the container with
    # mage
    ssi_service = await dffml.cached_download_unpack_archive(
        url,
        cache_dir.joinpath("ssi-service." + ''.join(pathlib.Path(url).suffixes)),
        cache_dir.joinpath("ssi-service-download"),
        hash_value,
    )
    try:
        # Directory which ssi-service source was download to
        kwargs = {
            "cwd": list(cache_dir.joinpath("ssi-service-download", "").glob("*"))[0],
        }

        from pprint import pprint
        pprint(list(golang.rglob("*")))

        os.environ["GOROOT"] = str(golang / "go")
        os.environ["GOPATH"] = str(ssi_service / ".gopath")
        os.environ["GOBIN"] = str(ssi_service / ".gopath" / "bin")

        with dffml.prepend_to_path(
            mage,
            golang / "go" / "bin",
        ):

            os.system("bash")

            await dffml.run_command([
                "mage",
                "cbt",
            ], logger=self.logger, **kwargs)

        print(kwargs)
        yield None
        return

        # Body of run_command

        # Combination of stdout and stderr
        cmd = [
            "init",
        ]
        logger = self.logger

        output = []
        if logger is not None:
            logger.debug(f"Running {cmd}, {kwargs}")
        async for event, result in dffml.exec_subprocess(cmd, **kwargs):
            if event == dffml.Subprocess.CREATED:
                # Set proc when created
                proc = result
            elif event in [dffml.Subprocess.STDOUT_READLINE, dffml.Subprocess.STDERR_READLINE]:
                # Log line read
                if logger is not None:
                    logger.debug(f"{cmd}: {event}: {result.decode().rstrip()}")
                # Append to output in case of error
                output.append(result)
            # Raise if anything goes wrong
            elif event == dffml.Subprocess.COMPLETED and result != 0:
                raise RuntimeError(repr(cmd) + ": " + b"\n".join(output).decode())
            print(event, result)
            breakpoint()

        yield ssi_service
    finally:
        # TODO Stop ssi_service
        pass
    # TODO Output chain to file(s)


@dffml.op(
    name="ssi_service.import.gateway",
    inputs={},
    outputs={},
    config_cls=SSIServiceConfig,
    imp_enter={
        "ssi_service": lambda self: download_ssi_service(
            self,
            self.config.download_url,
            self.config.download_hash,
            self.config.cache_dir,
        ),
    }
)
class ssi_service_import_gateway(dffml.OperationImplementationContext):
    """
    Takes inputs and puts them in firely

    We'll use the SSIService Gateway interface

    We can have our imp_enter dump chain to cold storage

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
    >>> dataflow = DataFlow.auto(last_path, ssi_service_import_gateway)
    >>> dataflow.operations[ssi_service_import_gateway.op.name] = ssi_service_import_gateway.op._replace(
    ...     inputs={last_path.op.outputs["last"].name: last_path.op.outputs["last"]},
    ... )
    >>> dataflow.update(auto_flow=True)
    >>>
    >>> async def main():
    ...     async for ctx, results in run(
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
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print(self, inputs)
        print(self.parent.ssi_service)
        return
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

        return

@dffml.op(
    name="ssi_service.import.peerdid",
    inputs={},
    outputs={
        "result": dffml.Definition(name="peerdid", primitive="object"),
    },
    config_cls=SSIServiceConfig,
)
class ssi_service_import_peerdid(dffml.OperationImplementationContext):
    """
    TODO Create DID after we know format in cold storage.
    """
    async def run(self, inputs):
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

import unittest
import doctest
import sys

def load_tests(loader, tests, ignore):
    # tests.addTests(doctest.DocTestSuite(sys.modules[__name__]))
    return tests

import logging
logging.basicConfig(level=logging.DEBUG)
import asyncio
from dffml import *

URL = Definition(name="URL", primitive="string")

@op(
    inputs={"url": URL},
    outputs={"last": Definition("last_element_in_path", primitive="string")},
)
def last_path(url):
    return {"last": url.split("/")[-1]}

dataflow = DataFlow.auto(last_path, ssi_service_import_gateway)
dataflow.operations[ssi_service_import_gateway.op.name] = ssi_service_import_gateway.op._replace(
    inputs={last_path.op.outputs["last"].name: last_path.op.outputs["last"]},
)
dataflow.update(auto_flow=True)

async def main():
    async for ctx, results in run(
        dataflow,
        {
            "run_subflow": [
                Input(value="https://github.com/intel/dffml", definition=URL)
            ]
        },
    ):
        print(results)

asyncio.run(main())
