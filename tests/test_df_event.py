import unittest
import logging

# logging.basicConfig(level=logging.DEBUG)

from dffml import (
    AsyncTestCase,
    DataFlow,
    Input,
    op,
    GetSingle,
    run,
    # Need to implement
    # EventType,
)


@op
def carnivore(string: str) -> str:
    if int(string) >= 42:
        return "beef"
    return "dead"


# 42 -> beef
# 41 -> dead


@op
def beef_to_feed(string: str) -> str:
    return string.replace("beef", "feed")


# beef -> feed
# dead -> dead


@op
def feed_in_string(string: str) -> bool:
    return "feed" in string


# feed -> True
# dead -> False

DATAFLOW = DataFlow(
    carnivore,
    beef_to_feed,
    feed_in_string,
    GetSingle,
    seed=[
        Input(
            value=[feed_in_string.op.outputs["result"].name],
            definition=GetSingle.op.inputs["spec"],
        ),
    ],
)
# Send the output of the carnivore function to beef_to_feed as the string input
DATAFLOW.flow[beef_to_feed.op.name].inputs["string"] = [
    {carnivore.op.name: "result"},
    # OR
    carnivore.op.outputs["result"].name,
]
# Send the output of the beef_to_feed function to feed_in_string as the string
# input
DATAFLOW.flow[feed_in_string.op.name].inputs["string"] = [
    {beef_to_feed.op.name: "result"}
]
DATAFLOW.update()


class TestDataFlowEventTypes(AsyncTestCase):
    async def test_event_types(self):
        async for ctx, event, data in run(
            DATAFLOW,
            {
                "context_A": [
                    Input(
                        value="42", definition=carnivore.op.inputs["string"],
                    ),
                ],
                "context_Z": [
                    Input(
                        value="0", definition=carnivore.op.inputs["string"],
                    ),
                ],
            },
        ):
            # Pre implementation of event types
            print("The results of", ctx, "are", data)
            continue
            # Post implementation of event types
            if event == EventType.OUTPUT:
                print("The results of", ctx, "are", data)
            elif event == EventType.INPUT:
                print("An input entered network for context", ctx, ":", data)
