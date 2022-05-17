"""
.. code-block:: console

    $ pip install peerdid

"""
import pprint as pprint_module

pprint = lambda *args, **kwargs: pprint_module.pprint(dict(args=args, kwargs=kwargs))

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

        pprint(golang.rglob("*"))

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
    name="system_context.run",
    inputs={},
    outputs={},
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
    ... def run_scan(url):
    ...     return {"last": url.split("/")[-1]}
    >>>
    >>> dataflow = DataFlow.auto(run_scan, ssi_service_import_gateway)
    >>> dataflow.operations[ssi_service_import_gateway.op.name] = ssi_service_import_gateway.op._replace(
    ...     inputs={run_scan.op.outputs["last"].name: run_scan.op.outputs["last"]},
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


# # Open Architecture Calling Convention
#
# "top level system context" means the first call into the open architecture.
# Once within the callee, the caller is referred to as the "parent
# system context". The callee should only be referred to as the system context,
# unless we are talking about in relation to it being a caller itself of a sub
# context it launches or manages. If it begins setting up a callee via forming
# of a manifest. We will start referring to it as a "parent system
# context" within the context of its relationship to it's new potential child.
# A strategic plan which suggests a system context will be a parent system
# context in the provenance data of the system context which chooses to run that
# suggested context. A context can have multiple parents. Only one of them can
# be a context with stage "execute".
#
# - Entity for top level system context is a `did:key:`
#   - Load via overlay given on call (dffml.run(), CLI, HTTP API execution:
#     think of new request creates new top level system context, because are
#     going to be running some flow to respond to an event.)
#     - In the event that multiple parties are involved in execution of the top
#       level system context equally. An ad-hoc organization will be formed if
#       it's not already being referenced. The entity for that org will be used.

import sys


@dffml.config
class EncyptedPrivateKey:
    passphrase: bytes = dffml.field(
        "Passphrase to encrypt/decypt private key",
    )
    comment: str = dffml.field(
        "Comment for generated key",
        default="no-comment",
    )


import jwcrypto.jwk


# Imp enter could be run dataflow which either connects to remote ssi_service or
# downloads and runs (ssh tunnels, proxies, etc.)
# TODO Remove context manager when we fix op imp_enter and ctx_enter to not
# attempt context entry before setting return value on parent key given if
# return value is not a context manager. We want to call coroutines instead of
# entering their context.
@contextlib.asynccontextmanager
async def download_step_ca(self, cache_dir):
    # TODO Implement load from file(s) on start if given (another pathlib.Path
    # argument after cache_dir)
    # TODO For generic case we should remove any query string found after last
    # suffix (?..., #...)

    # cosign_url = ""
    # cosign_sha = ""
    # cosign = await dffml.cached_download_unpack_archive(
    #     cosign_url,
    #     cache_dir.joinpath("cosign." + ''.join(pathlib.Path(cosign_url).suffixes)),
    #     cache_dir.joinpath("cosign-download"),
    #     cosign_sha,
    # )
    # SSI Service is packaged as docker but we must build the container with
    # stepca
    # stepca_sig_path = await dffml.cached_download(
    #     "https://github.com/smallstep/certificates/releases/download/v0.19.0/step-ca_linux_0.19.0_amd64.tar.gz.sig",
    #     stepca_sig.joinpath("stepca.sig"),
    #     "0221ea842fe7936945493a68db5eeda4b6d13d4ce89bd1e8ecaeb87475d7f0dc7b5e73c8d77443273485f2d48b31a99f",
    # )
    step_url = "https://dl.step.sm/gh-release/cli/gh-release-header/v0.19.0/step_linux_0.19.0_amd64.tar.gz"
    step_sha = "415e81cd3bdffc0727d12f8c2a2a386626ba343d0a66c9e0106fb794ebcaba57a74cbc56c6a7a8dd80d52e07d0e546dd"
    step_archive_path = cache_dir.joinpath("step" + ''.join(pathlib.Path(step_url).suffixes))
    # TODO(security) Add in cosign validation after download, before extract
    step = await dffml.cached_download_unpack_archive(
        step_url,
        step_archive_path,
        cache_dir.joinpath("step-download"),
        step_sha,
    )
    stepca_url = "https://github.com/smallstep/certificates/releases/download/v0.19.0/step-ca_linux_0.19.0_amd64.tar.gz"
    stepca_sha = "dcff858973910eefd893ff571a266187658e07435a6a97559c3c9314f24f6cdeb0d3ded9203c1717d677ac12af80bc1f"
    stepca_archive_path = cache_dir.joinpath("stepca" + ''.join(pathlib.Path(stepca_url).suffixes))
    # TODO(security) Add in cosign validation after download, before extract
    stepca = await dffml.cached_download_unpack_archive(
        stepca_url,
        stepca_archive_path,
        cache_dir.joinpath("stepca-download"),
        stepca_sha,
    )
    # await dffml.run_command([
    #     cosign.joinpath("cosign"),
    #     "cosign",
    #     "verify-blob",
    #     "-key",
    #     "https://raw.githubusercontent.com/smallstep/certificates/master/cosign.pub",
    #     "-signature",
    #     stepca_sig_path,
    #     stepca_archive_path,
    # ], logger=self.logger)
    binaries = [
        path
        for path in stepca.rglob("step-ca")
        if path.name == "step-ca"
    ] + [
        path
        for path in step.rglob("step")
        if path.name == "step"
    ]
    with dffml.prepend_to_path(*[
        str(binary.parent)
        for binary in binaries
    ]):
        yield binaries


@dffml.op(
    name="ssi_service.import.peerdid",
    inputs={},
    outputs={
        "result": dffml.Definition(name="peerdid", primitive="object"),
    },
    config_cls=EncyptedPrivateKey,
    imp_enter={
        "step_ca": lambda self: download_step_ca(
            self,
            CACHED_DOWNLOADS,
        ),
    }
)
class ssi_service_import_peerdid(dffml.OperationImplementationContext):
    """
    TODO Create DID after we know format in cold storage.
    """
    async def run(self, inputs):
        # Create ssh key in pem format.
        # TODO Make this an operation which could be added to flow. Eventually
        # support generating key using JWCypto.
        import tempfile
        with tempfile.TemporaryDirectory() as tempdir:
            tempdir_path = pathlib.Path(tempdir)
            # The path to the root private key
            identity_root_key_path = tempdir_path.joinpath("identity_root_key")
            identity_root_key_pem_path = tempdir_path.joinpath("identity_root_key.pem")
            pprint(
                identity_root_key_path,
                identity_root_key_pem_path,
            )
            # TODO Make more of these arguments configurable in the future
            # (subprocess operation(implementation) network.
            await dffml.run_command(
                [
                    "openssl",
                    "genpkey",
                    "-algorithm",
                    "ed25519",
                    "-outform",
                    "PEM",
                    "-out",
                    identity_root_key_pem_path,
                ],
                logger=self.logger,
                cwd=tempdir,
            )
            pprint(
                identity_root_key_pem_path.read_bytes(),
            )
            # await dffml.run_command(
            #     [
            #         "ssh-keygen",
            #         "-p"
            #         "-t",
            #         "ed25519",
            #         "-f",
            #         identity_root_key_path,
            #         "-N",
            #         self.parent.config.passphrase,
            #         "-C",
            #         self.parent.config.comment,
            #         "-m",
            #         "pkcs8",
            #     ],
            #     logger=self.logger,
            #     cwd=tempdir,
            # )
            # identity_root_key_pem_path.write_bytes(
            #     identity_root_key_path.read_bytes().replace(
            #     b"BEGIN OPENSSH PRIVATE KEY", b"BEGIN CERTIFICATE").replace(
            #     b"END OPENSSH PRIVATE KEY", b"END CERTIFICATE"))
            identity_root_key_path.write_bytes(b"")
            # TODO Windows
            identity_root_key_path.chmod(0o600)
            identity_root_key_path.write_bytes(
                identity_root_key_pem_path.read_bytes()
            )
            pprint(
                identity_root_key_path.read_bytes(),
            )
            # await dffml.run_command(
            #     [
            #         "ssh-keygen",
            #         "-p",
            #         "-t",
            #         "ed25519",
            #         "-f",
            #         identity_root_key_path,
            #         "-N",
            #         self.parent.config.passphrase,
            #         "-m",
            #         "pem",
            #     ],
            #     logger=self.logger,
            #     cwd=tempdir,
            # )

            gen_key = "step crypto keypair --no-password --insecure --kty OKP --crv Ed25519 ssh_host_key.pem ssh_host_key"
            await dffml.run_command(
                gen_key.split(),
                logger=self.logger,
                cwd=tempdir,
            )
            format_key = "step crypto key format --ssh ssh_host_key.pem"
            await dffml.run_command(
                format_key.split(),
                logger=self.logger,
                cwd=tempdir,
            )
            # Copy key to file to overwrite with key in pem format
            # Read in key contents
            identity_root_key_pem_path = tempdir_path.joinpath("ssh_host_key.pem")
            identity_root_key_pem_contents = identity_root_key_pem_path.read_bytes()
            # Import key to JWK format
            # Initial support for PEM format PKCS8 ED25519 key
            pprint(
                files=list(tempdir_path.rglob("*")),
                identity_root_key=identity_root_key_path.read_bytes(),
                identity_root_pem_key=identity_root_key_pem_contents,
                password=self.parent.config.passphrase,
            )
            keys = {}
            keys['signing'] = jwcrypto.jwk.JWK()
            keys['signing'].import_from_pem(
                identity_root_key_pem_contents,
                # password=self.parent.config.passphrase,
            )
            print(keys['signing'])
            # TODO Make these arguments configurable in the future (subprocess
            # operation(implementation) network.
            # We cannot use the same key to both sign and encrypt.
            # See peerdid readme and
            # https://libsodium.gitbook.io/doc/quickstart#how-can-i-sign-and-encrypt-using-the-same-key-pair
            # pprint(**keys['signing'].export_private(as_dict=True))
            # TODO These keys are not quantum safe, see KERI
            keys['encryption'] = jwcrypto.jwk.JWK.generate(kty='OKP', crv='X25519')

            pprint(encryption=keys['encryption'].export(private_key=True))
            encryption_keys = [
                VerificationMaterialAgreement(
                    type=VerificationMethodTypeAgreement.JSON_WEB_KEY_2020,
                    format=VerificationMaterialFormatPeerDID.JWK,
                    # value=keys['encryption'],
                    value=keys['encryption'].export(private_key=True),
                )
            ]
            signing_keys = [
                VerificationMaterialAuthentication(
                    type=VerificationMethodTypeAuthentication.ED25519_VERIFICATION_KEY_2018,
                    format=VerificationMaterialFormatPeerDID.JWK,
                    value=keys['signing'],
                )
            ]
            dataflow = self.octx.config.dataflow
            import json
            manifest = dffml.export(dataflow)
            manifest = {}
            encoded_manifest = json.dumps(manifest)
            service = {
                            "id": "#architecture",
                            "type": "OpenArchitecture",
                            "serviceEndpoint": encoded_manifest,
                            "routingKeys": ["did:example:somemediator#somekey1"],
                            "accept": ["didcomm/v2", "didcomm/aip2;env=rfc587"]
                        }
            service = json.dumps(service)

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

        BOB_DID = did_doc_algo_0 = DIDDocPeerDID.from_json(did_doc_algo_0_json)
        ALICE_DID = did_doc_algo_2 = DIDDocPeerDID.from_json(did_doc_algo_2_json)
        print("did_doc_algo_0 as object:" + str(did_doc_algo_0.to_dict()))
        print("==================================")
        print("did_doc_algo_2 as object:" + str(did_doc_algo_2.to_dict()))

        # ALICE
        import didcomm.message
        message = didcomm.message.Message(
            body=manifest,
            id="Input.id-1234567890",
            type="open-architecture/0.0.1",
            frm=ALICE_DID,
            to=[BOB_DID],
        )
        import didcomm.pack_signed

        import didcomm.did_doc.did_resolver

        class DIDResolverPeerDID(didcomm.did_doc.did_resolver.DIDResolver):

            async def resolve(self, did: DID) -> Optional[DIDDoc]:
                # This resolver should be used in the input network of the
                # running context. As well as within a background operation
                # which pulls in new dids (maybe just autostart operations
                # yielding inputs).
                await self.source.record(did)
                # request DID Doc in JWK format
                did_doc_json = peer_did.resolve_peer_did(did, format=VerificationMaterialFormatPeerDID.JWK)
                did_doc = DIDDocPeerDID.from_json(did_doc_json)

                return DIDDoc(
                    did=did_doc.did,
                    key_agreement_kids=did_doc.agreement_kids,
                    authentication_kids=did_doc.auth_kids,
                    verification_methods=[
                        VerificationMethod(
                            id=m.id,
                            type=VerificationMethodType.JSON_WEB_KEY_2020,
                            controller=m.controller,
                            verification_material=VerificationMaterial(
                                format=VerificationMaterialFormat.JWK,
                                value=json.dumps(m.ver_material.value)
                            )
                        )
                        for m in did_doc.authentication + did_doc.key_agreement
                    ],
                    didcomm_services=[
                        DIDCommService(
                            id=s.id,
                            service_endpoint=s.service_endpoint,
                            routing_keys=s.routing_keys,
                            accept=s.accept
                        )
                        for s in did_doc.service
                        if isinstance(s, DIDCommServicePeerDID)
                    ] if did_doc.service else []
                )

        packed_msg = await didcomm.pack_signed.pack_signed(
            message=message,
            sign_frm=ALICE_DID,
            resolvers_config=ResolversConfig(
                secrets_resolver=SecretsResolverDemo(),
                did_resolver=DIDResolverPeerDID(),
            ),
        )
        packed_msg = pack_result.packed_msg
        print(f"Publishing ${packed_msg}")

        # BOB
        import didcomm.unpack
        unpack_result = await didcomm.unpack.unpack(packed_msg)
        print(f"Got ${unpack_result.message} message signed as "
              f"${unpack_result.metadata.signed_message}")

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

@op
def run_scan(url: str) -> dict:
    return {
        "high": 5,
    }


@dffml.config
class SystemContext:
    # TODO DataFlow is one type of Architecture. Base class for Architecture is
    # OpenArchitecture. DataFlow should register itself under OpenArchitecture
    # plugins (entry point)
    parent: 'SystemContext'
    inputs: List[dffml.BaseInputSetContext]
    architecture: dffml.DataFlow
    orchestrator: dffml.BaseOrchestrator

    def valid(self):
        """
        TODO Ensure all inputs in architecture allowlist are mapped to input
        sources.
        """

@op(
    inputs={
        "ctx": Definition(
            name="SystemContext",
            primitive="object",
            spec=SystemContext,
        ),
    },
)
async def run_system_context(
    ctx: SystemContext,
) -> AsyncIterator[Tuple[BaseInputSetContext, Dict[str, Any]]]:
    async for ctx, results in dffml.run(
        ctx.architecture.dataflow,
        *ctx.contexts,
        orchestrator=ctx.orchestrator,
    ):
        """
        TODO: Evaluate need to add additional run keyword arguments to ctx
        strict: bool = True,
        ctx: Optional[BaseInputSetContext] = None,
        halt: Optional[asyncio.Event] = None,
        """
        yield ctx, results


ssi_service_import = ssi_service_import_peerdid
# ssi_service_import = ssi_service_import_gateway
dataflow = DataFlow.auto(
    run_scan,
    run_system_context,
    seed=[
        Input(
            # TODO Just like our Input objects (should can we share here / auto
            # populate?)
            value=SystemContext(
                parent=None,
                contexts=[
                    MemoryInputSet(
                        ctx=StringInputSetContext("background_default"),
                        inputs=[
                            Input(
                                value=,
                                definition=,
                            ),
                        ],
                    )
                },
            ),
            definition=run_system_context.op.inputs["ctx"],
        ),
    ]
)

from typing import Dict, Any

from ..base import config
from ..df.base import op, OperationImplementationContext
from ..df.types import DataFlow, Input, Definition


class InvalidCustomRunDataFlowContext(Exception):
    """
    Thrown when custom inputs for dffml.dataflow.run do not list an input with
    string as its primitive as the first input.
    """


class InvalidCustomRunDataFlowOutputs(Exception):
    """
    Thrown when outputs for a custom dffml.dataflow.run do not match that of
    it's subflow.
    """


@config
class RunDataFlowConfig:
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
    config_cls=RunDataFlowConfig,
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
    >>> dataflow.configs[run_dataflow.op.name] = RunDataFlowConfig(subflow)
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
    >>> dataflow.configs[run_dataflow.op.name] = RunDataFlowConfig(subflow)
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
            raise InvalidCustomRunDataFlowContext(ctx_definition.export())

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
                    raise InvalidCustomRunDataFlowOutputs(
                        ctx_definition.export()
                    )
                return result

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Support redefinition of operation
        if self.parent.op.inputs == DEFAULT_INPUTS:
            return await self.run_default(inputs["inputs"])
        else:
            return await self.run_custom(inputs)
    ],
)
dataflow.configs[ssi_service_import.op.name] = EncyptedPrivateKey(
    passphrase=os.environ["KEY_PASSPHRASE"].encode(),
)
dataflow.operations[ssi_service_import.op.name] = ssi_service_import.op._replace(
    inputs={run_scan.op.outputs["result"].name: run_scan.op.outputs["result"]},
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
