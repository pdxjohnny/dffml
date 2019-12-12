import sys

from dffml.df.types import Input, DataFlow
from dffml.df.base import operation_in, opimp_in, Operation
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetMulti
from dffml.util.asynctestcase import AsyncTestCase

from dffml_operation_dockerhub.operations import *

OPIMPS = opimp_in(sys.modules[__name__])

DOCKER_HUB_API_URL = "https://store.docker.com/api/content/v1/"


class TestOperations(AsyncTestCase):
    async def test_run(self):
        dataflow = DataFlow.auto(*OPIMPS)
        # Allow inputs from seed and from dockerhub_scrape_page
        dataflow.flow["url_to_mapping"].inputs["url"].append("seed")
        dataflow.update_by_origin()
        # Search URL to start with
        search_url: str = f"{DOCKER_HUB_API_URL}/products/search?&page_size=25&q=&type=image"
        urls_check = [search_url] + [
            f"{DOCKER_HUB_API_URL}products/search/?type=image&page={i}&page_size=25"
            for i in range(2, 19)
        ]
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(dataflow) as octx:
                async for ctx, results in octx.run(
                    [
                        Input(
                            value=search_url,
                            definition=url_to_mapping.op.inputs["url"],
                        ),
                        Input(
                            value=[
                                dockerhub_scrape_page.op.outputs["urls"].name
                            ],
                            definition=GetMulti.op.inputs["spec"],
                        ),
                    ]
                ):
                    for url_check in urls_check:
                        self.assertIn(
                            url_check,
                            results[
                                dockerhub_scrape_page.op.outputs["urls"].name
                            ],
                        )
