import abc
import inspect
import collections
import pkg_resources
from typing import (
    AsyncIterator,
    Dict,
    List,
    Tuple,
    Any,
    NamedTuple,
    Union,
    Optional,
    Set,
)
from dataclasses import dataclass, is_dataclass, replace
from contextlib import asynccontextmanager

from .exceptions import NotOpImp
from .types import Operation, Input, Parameter, Stage, Definition, NO_DEFAULT

from .log import LOGGER

from ..base import (
    BaseConfig,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)
from ..util.cli.arg import Arg
from ..util.data import get_origin, get_args
from ..util.asynchelper import context_stacker
from ..util.entrypoint import base_entry_point
from ..util.entrypoint import load as load_entrypoint


primitive_types = (int, float, str, bool, dict, list, bytes)
# Used to convert python types in to their programming language agnostic
# names
# TODO Combine with logic in dffml.util.data
primitive_convert = {dict: "map", list: "array"}


class BaseDataFlowObjectContext(BaseDataFlowFacilitatorObjectContext):
    """
    Data Flow Object Contexts are instantiated by being passed their
    config, and their parent, a BaseDataFlowObject.
    """

    def __init__(
        self, config: BaseConfig, parent: "BaseDataFlowObject"
    ) -> None:
        self.config = config
        self.parent = parent


class BaseDataFlowObject(BaseDataFlowFacilitatorObject):
    """
    Data Flow Objects create their child contexts' by passing only itself as an
    argument to the child's __init__ (of type BaseDataFlowObjectContext).
    """

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        if hasattr(cls, "CONFIG"):
            return super(BaseDataFlowObject, cls).args(args, *above)
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        if hasattr(cls, "CONFIG"):
            return super(BaseDataFlowObject, cls).config(config, *above)
        return BaseConfig()


class OperationImplementationContext(BaseDataFlowObjectContext):
    def __init__(
        self,
        parent: "OperationImplementation",
        ctx: "BaseInputSetContext",
        octx: "BaseOrchestratorContext",
    ) -> None:
        self.parent = parent
        self.ctx = ctx
        self.octx = octx

    @property
    def config(self):
        """
        Alias for self.parent.config
        """
        return self.parent.config

    @abc.abstractmethod
    async def run(self, inputs: Dict[str, Any]) -> Union[bool, Dict[str, Any]]:
        """
        Implementation of the operation goes here. Should take and return a dict
        with keys matching the input and output parameters of the Operation
        object associated with this operation implementation context.
        """

    @asynccontextmanager
    async def subflow(self, dataflow):
        """
        Registers subflow `dataflow` with parent flow and yields an instance of `BaseOrchestratorContext`

        >>> async def my_operation(arg):
        ...     async with self.subflow(self.config.dataflow) as octx:
        ...         return octx.run({"ctx_str": []})
        """
        async with self.octx.parent(dataflow) as octx:
            self.octx.subflows[self.parent.op.instance_name] = octx
            yield octx


class FailedToLoadOperationImplementation(Exception):
    """
    Raised when an OperationImplementation wasn't found to be registered with
    the dffml.operation entrypoint.
    """


class OpCouldNotDeterminePrimitive(Exception):
    """
    op could not determine the primitive of the parameter
    """


@base_entry_point("dffml.operation", "opimp")
class OperationImplementation(BaseDataFlowObject):
    def __init__(self, config: "BaseConfig") -> None:
        super().__init__(config)
        if not getattr(self, "op", False):
            raise ValueError(
                "OperationImplementation's may not be "
                + "created without an `op`"
            )

    def __call__(
        self, ctx: "BaseInputSetContext", octx: "BaseOrchestratorContext"
    ) -> OperationImplementationContext:
        return self.CONTEXT(self, ctx, octx)

    @classmethod
    def add_orig_label(cls, *above):
        return list(above) + cls.op.name.split("_")

    @classmethod
    def add_label(cls, *above):
        return list(above) + cls.op.name.split("_")

    @classmethod
    def _imp(cls, loaded):
        """
        Returns the operation implementation from a loaded entrypoint object, or
        None if its not an operation implementation or doesn't have the imp
        parameter which is an operation implementation.
        """
        for obj in [getattr(loaded, "imp", None), loaded]:
            if inspect.isclass(obj) and issubclass(obj, cls):
                return obj
        if (
            inspect.isfunction(loaded)
            or inspect.isgeneratorfunction(loaded)
            or inspect.iscoroutinefunction(loaded)
            or inspect.isasyncgenfunction(loaded)
        ):
            return op(loaded).imp
        return None

    @classmethod
    def load(cls, loading: str = None):
        loading_classes = []
        # Load operations
        for i in pkg_resources.iter_entry_points(cls.ENTRYPOINT):
            if loading is not None and i.name == loading:
                loaded = cls._imp(i.load())
                if loaded is not None:
                    return loaded
            elif loading is None:
                loaded = cls._imp(i.load())
                if loaded is not None:
                    loading_classes.append(loaded)
        # Loading from entrypoint if ":" is in name
        if loading is not None and ":" in loading:
            loaded = next(load_entrypoint(loading, relative=True))
            loaded = cls._imp(loaded)
            return loaded
        if loading is not None:
            raise FailedToLoadOperationImplementation(
                "%s was not found in (%s)"
                % (
                    repr(loading),
                    ", ".join(list(map(lambda op: op.name, loading_classes))),
                )
            )
        return loading_classes


def create_definition(name, param_annotation, default=NO_DEFAULT):
    if param_annotation in primitive_types:
        return Definition(
            name=name,
            primitive=primitive_convert.get(
                param_annotation, param_annotation.__name__
            ),
            default=default,
        )
    elif get_origin(param_annotation) in [
        Union,
        collections.abc.AsyncIterator,
    ]:
        # If the annotation is of the form Optional
        return create_definition(name, list(get_args(param_annotation))[0])
    elif (
        get_origin(param_annotation) is list
        or get_origin(param_annotation) is dict
    ):
        # If the annotation are of the form List[MyDataClass] or Dict[str, MyDataClass]
        if get_origin(param_annotation) is list:
            primitive = "array"
            innerclass = list(get_args(param_annotation))[0]
        else:
            primitive = "map"
            innerclass = list(get_args(param_annotation))[1]

        if innerclass in primitive_types:
            return Definition(name=name, primitive=primitive, default=default)
        if is_dataclass(innerclass) or bool(
            inspect.isclass(innerclass)
            and issubclass(innerclass, tuple)
            and hasattr(innerclass, "_asdict")
        ):
            return Definition(
                name=name,
                primitive=primitive,
                default=default,
                spec=innerclass,
                subspec=True,
            )
    elif is_dataclass(param_annotation) or bool(
        inspect.isclass(param_annotation)
        and issubclass(param_annotation, tuple)
        and hasattr(param_annotation, "_asdict")
    ):
        # If the annotation is either a dataclass or namedtuple
        return Definition(
            name=name, primitive="map", default=default, spec=param_annotation,
        )

    raise OpCouldNotDeterminePrimitive(
        f"The primitive of {name} could not be determined"
    )


def op(
    *args,
    imp_enter=None,
    ctx_enter=None,
    config_cls=None,
    valid_return_none=True,
    **kwargs,
):
    """
    The ``op`` decorator creates a subclass of
    :py:class:`dffml.df.OperationImplementation` and assigns that
    ``OperationImplementation`` to the ``.imp`` parameter of the
    function it decorates.

    If the decorated object is not already a class which is a subclass of
    ``OperationImplementationContext``, it creates an
    :py:class:`dffml.df.OperationImplementationContext`
    and assigns it to the ``CONTEXT`` class parameter of the
    ``OperationImplementation`` which was created.

    Upon context entry into the ``OperationImplementation``, imp_enter is
    iterated over and the values in that ``dict`` are entered. The value yielded
    upon entry is assigned to a parameter in the ``OperationImplementation``
    instance named after the respective key.

    Examples
    --------

    >>> from dffml import Definition, Input, op
    >>> from typing import NamedTuple, List, Dict
    >>>
    >>> class Person(NamedTuple):
    ...     name: str
    ...     age: int
    ...
    >>> @op
    ... def cannotVote(p: List[Person]):
    ...     return list(filter(lambda person: person.age < 18, p))
    ...
    >>>
    >>> Input(
    ...     value=[
    ...         {"name": "Bob", "age": 20},
    ...         {"name": "Mark", "age": 21},
    ...         {"name": "Alice", "age": 90},
    ...     ],
    ...     definition=cannotVote.op.inputs["p"],
    ... )
    Input(value=[Person(name='Bob', age=20), Person(name='Mark', age=21), Person(name='Alice', age=90)], definition=cannotVote.inputs.p)
    >>>
    >>> @op
    ... def canVote(p: Dict[str, Person]) -> Dict[str, Person]:
    ...     return {
    ...         person.name: person
    ...         for person in filter(lambda person: person.age >= 18, p.values())
    ...     }
    ...
    >>>
    >>> Input(
    ...     value={
    ...         "Bob": {"name": "Bob", "age": 19},
    ...         "Alice": {"name": "Alice", "age": 21},
    ...         "Mark": {"name": "Mark", "age": 90},
    ...     },
    ...     definition=canVote.op.inputs["p"],
    ... )
    Input(value={'Bob': Person(name='Bob', age=19), 'Alice': Person(name='Alice', age=21), 'Mark': Person(name='Mark', age=90)}, definition=canVote.inputs.p)
    >>>
    >>> Input(
    ...     value={
    ...         "Bob": {"name": "Bob", "age": 19},
    ...         "Alice": {"name": "Alice", "age": 21},
    ...         "Mark": {"name": "Mark", "age": 90},
    ...     },
    ...     definition=canVote.op.outputs["result"],
    ... )
    Input(value={'Bob': Person(name='Bob', age=19), 'Alice': Person(name='Alice', age=21), 'Mark': Person(name='Mark', age=90)}, definition=canVote.outputs.result)
    """

    def wrap(func):
        if not "name" in kwargs:
            name = func.__name__
            module_name = inspect.getmodule(func).__name__
            if module_name != "__main__":
                name = f"{module_name}:{name}"
            # Check if it's already been registered as another name
            for i in pkg_resources.iter_entry_points(Operation.ENTRYPOINT):
                entrypoint_load_path = i.module_name + ":" + ".".join(i.attrs)
                # If it has, then let that name take precedence
                if entrypoint_load_path == name:
                    name = i.name
                    break
            kwargs["name"] = name
        # TODO Make this grab from the defaults for Operation
        if not "conditions" in kwargs:
            kwargs["conditions"] = []

        sig = inspect.signature(func)
        # Check if the function uses the operation implementation context
        uses_self = bool(
            (sig.parameters and list(sig.parameters.keys())[0] == "self")
            or imp_enter is not None
            or ctx_enter is not None
            or (
                [
                    name
                    for name, param in sig.parameters.items()
                    if param.annotation is OperationImplementationContext
                ]
            )
        )
        # Check if the function uses the operation implementation config
        # This exists because eventually we will make non async functions
        # wrapped with op run with loop.run_in_executor when that happens it's
        # likely that self won't be serializeable into the thread / process.
        # Config's are guaranteed to be serializable, therefore this lets us
        # define operations that have configs and needs to access them when
        # running within another thread.
        uses_config = None
        if config_cls is not None:
            for name, param in sig.parameters.items():
                if param.annotation is config_cls:
                    uses_config = name

        # Definition for inputs of the function
        if not "inputs" in kwargs:
            sig = inspect.signature(func)
            kwargs["inputs"] = {}
            for name, param in sig.parameters.items():
                if name == "self":
                    continue
                name_list = [kwargs["name"], "inputs", name]

                kwargs["inputs"][name] = create_definition(
                    ".".join(name_list),
                    param.annotation,
                    NO_DEFAULT
                    if param.default is inspect.Parameter.empty
                    else param.default,
                )

        auto_def_outputs = False
        # Definition for return type of a function
        if not "outputs" in kwargs:
            return_type = inspect.signature(func).return_annotation
            if return_type not in (None, inspect._empty):
                name_list = [kwargs["name"], "outputs", "result"]

                kwargs["outputs"] = {
                    "result": create_definition(
                        ".".join(name_list), return_type
                    )
                }
                auto_def_outputs = True

        func.op = Operation(**kwargs)
        func.ENTRY_POINT_NAME = ["operation"]
        cls_name = (
            func.op.name.replace(".", " ")
            .replace("_", " ")
            .title()
            .replace(" ", "")
        )

        # Create the test method which creates the contexts and runs
        async def test(**kwargs):
            async with func.imp(BaseConfig()) as obj:
                async with obj(None, None) as ctx:
                    return await ctx.run(kwargs)

        func.test = test

        class Implementation(
            context_stacker(OperationImplementation, imp_enter)
        ):
            def __init__(self, config):
                if config_cls is not None and isinstance(config, dict):
                    if getattr(config_cls, "_fromdict", None) is not None:
                        # Use _fromdict method if it exists
                        config = config_cls._fromdict(**config)
                    else:
                        # Otherwise expand if existing config is a dict
                        config = config_cls(**config)
                super().__init__(config)

        if config_cls is not None:
            Implementation.CONFIG = config_cls

        if inspect.isclass(func) and issubclass(
            func, OperationImplementationContext
        ):
            func.imp = type(
                f"{cls_name}Implementation",
                (Implementation,),
                {"op": func.op, "CONTEXT": func},
            )
            return func
        else:

            class ImplementationContext(
                context_stacker(OperationImplementationContext, ctx_enter)
            ):
                async def run(
                    self, inputs: Dict[str, Any]
                ) -> Union[bool, Dict[str, Any]]:
                    # Add config to inputs if it's used by the function
                    if uses_config is not None:
                        inputs[uses_config] = self.parent.config
                    # If imp_enter or ctx_enter exist then bind the function to
                    # the ImplementationContext so that it has access to the
                    # context and it's parent
                    if uses_self:
                        # We can't pass self to functions running in threads
                        # Its not thread safe!
                        bound = func.__get__(self, self.__class__)
                        result = bound(**inputs)
                        if inspect.isawaitable(result):
                            result = await result
                    elif inspect.iscoroutinefunction(func):
                        result = await func(**inputs)
                    else:
                        # TODO Add auto thread pooling of non-async functions
                        result = func(**inputs)
                    if auto_def_outputs and len(self.parent.op.outputs) == 1:
                        if inspect.isasyncgen(result):

                            async def convert_asyncgen(outputs):
                                async for yielded_output in outputs:
                                    yield {
                                        list(self.parent.op.outputs.keys())[
                                            0
                                        ]: yielded_output
                                    }

                            result = convert_asyncgen(result)
                        elif result is not None and valid_return_none:
                            result = {
                                list(self.parent.op.outputs.keys())[0]: result
                            }
                    return result

            func.imp = type(
                f"{cls_name}Implementation",
                (Implementation,),
                {
                    "op": func.op,
                    "CONTEXT": type(
                        f"{cls_name}ImplementationContext",
                        (ImplementationContext,),
                        {},
                    ),
                },
            )
            return func

    # This case handles if op was called with no arguments, args will be a tuple
    # with one element, that element being func, the function to wrap.
    if args:
        return wrap(args[0])

    return wrap


def opimp_name(item):
    if (
        inspect.isclass(item)
        and issubclass(item, OperationImplementation)
        and item is not OperationImplementation
    ):
        return item.op.name
    if (
        inspect.ismethod(item)
        and issubclass(item.__self__, OperationImplementationContext)
        and item.__name__ == "imp"
    ):
        return item.__self__.op.name
    raise NotOpImp(item)


def isopimp(item):
    """
    Similar to inspect.isclass and that family of functions. Returns true if
    item is a subclass of OperationImpelmentation.
    """
    return bool(
        (
            inspect.isclass(item)
            and issubclass(item, OperationImplementation)
            and item is not OperationImplementation
        )
        or (
            inspect.ismethod(item)
            and issubclass(item.__self__, OperationImplementationContext)
            and item.__name__ == "imp"
        )
    )


def isoperation(item):
    """
    Similar to inspect.isclass and that family of functions. Returns true if
    item is an instance of Operation.
    """
    return bool(isinstance(item, Operation) and item is not Operation)


def isopwraped(item):
    """
    Similar to inspect.isclass and that family of functions. Returns true if a
    function has been wrapped with `op`.
    """
    return bool(
        getattr(item, "op", False)
        and getattr(item, "imp", False)
        and isoperation(item.op)
        and isopimp(item.imp)
    )


def mk_base_in(predicate):
    """
    Creates the functions which use inspect getmembers to extract operations or
    implementations from some list which.
    """

    def base_in(to_check):
        return list(
            map(
                lambda item: item[1],
                inspect.getmembers(to_check, predicate=predicate),
            )
        )

    return base_in


opwraped_in = mk_base_in(isopwraped)

__operation_in = mk_base_in(isoperation)


def operation_in(iterable):
    return __operation_in(iterable) + list(
        map(lambda item: item.op, opwraped_in(iterable))
    )


__opimp_in = mk_base_in(isopimp)


def opimp_in(iterable):
    return __opimp_in(iterable) + list(
        map(lambda item: item.imp, opwraped_in(iterable))
    )


class BaseKeyValueStoreContext(BaseDataFlowObjectContext):
    """
    Abstract Base Class for key value storage context
    """

    @abc.abstractmethod
    async def get(self, key: str) -> Union[bytes, None]:
        """
        Get a value from the key value store
        """

    @abc.abstractmethod
    async def set(self, name: str, value: bytes):
        """
        Get a value in the key value store
        """


@base_entry_point("dffml.kvstore", "kvstore")
class BaseKeyValueStore(BaseDataFlowObject):
    """
    Abstract Base Class for key value storage
    """


class BaseContextHandle(abc.ABC):
    def __init__(self, ctx: "BaseInputSetContext") -> None:
        self.ctx = ctx
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    def as_string(self) -> str:
        pass


class BaseInputSetContext(abc.ABC):
    @abc.abstractmethod
    async def handle(self) -> BaseContextHandle:
        pass


class StringContextHandle(BaseContextHandle):
    def as_string(self) -> str:
        return self.ctx.as_string


class StringInputSetContext(BaseInputSetContext):
    def __init__(self, as_string):
        self.as_string = as_string

    async def handle(self) -> BaseContextHandle:
        return StringContextHandle(self)

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return repr(self)


class BaseInputSetConfig(NamedTuple):
    ctx: BaseInputSetContext


class BaseInputSet(abc.ABC):
    def __init__(self, config: BaseInputSetConfig) -> None:
        self.config = config
        self.ctx = config.ctx
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def add(self, item: Input) -> None:
        """
        Add an input to the input set.
        """

    @abc.abstractmethod
    async def definitions(self) -> Set[Definition]:
        pass

    @abc.abstractmethod
    async def inputs(self) -> AsyncIterator[Input]:
        pass

    async def _asdict(self) -> Dict[str, Any]:
        """
        Returns an input definition name to input value dict
        """
        return {
            item.definition.name: item.value async for item in self.inputs()
        }

    @abc.abstractmethod
    async def remove_input(self, item: Input) -> None:
        """
        Removes item from input set
        """

    @abc.abstractmethod
    async def remove_unvalidated_inputs(self) -> "BaseInputSet":
        """
        Removes `unvalidated` inputs from internal list and returns the same.
        """


class BaseParameterSetConfig(NamedTuple):
    ctx: BaseInputSetContext


class BaseParameterSet(abc.ABC):
    def __init__(self, config: BaseParameterSetConfig) -> None:
        self.config = config
        self.ctx = config.ctx
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    @abc.abstractmethod
    async def parameters(self) -> AsyncIterator[Parameter]:
        pass

    @abc.abstractmethod
    async def inputs_and_parents_recursive(self) -> AsyncIterator[Input]:
        pass

    async def _asdict(self) -> Dict[str, Any]:
        """
        Returns an parameter definition name to parameter value dict
        """
        return {
            parameter.key: parameter.value
            async for parameter in self.parameters()
        }


class BaseDefinitionSetContext(BaseDataFlowObjectContext):
    def __init__(
        self,
        config: BaseConfig,
        parent: "BaseInputNetworkContext",
        ctx: "BaseInputSetContext",
    ) -> None:
        super().__init__(config, parent)
        self.ctx = ctx

    @abc.abstractmethod
    async def inputs(self, Definition: Definition) -> AsyncIterator[Input]:
        """
        Asynchronous iterator of all inputs within a context, which are of a
        definition.
        """


class BaseInputNetworkContext(BaseDataFlowObjectContext):
    """
    Abstract Base Class for context managing input_set
    """

    @abc.abstractmethod
    async def add(self, input_set: BaseInputSet):
        """
        Adds new input set to the network
        """

    @abc.abstractmethod
    async def ctx(self) -> BaseInputSetContext:
        """
        Returns when a new input set context has entered the network
        """

    @abc.abstractmethod
    async def added(self, ctx: BaseInputSetContext) -> BaseInputSet:
        """
        Returns when a new input set has entered the network within a context
        """

    @abc.abstractmethod
    async def definition(
        self, ctx: BaseInputSetContext, definition: str
    ) -> Definition:
        """
        Search for the definition within a context given its name as a string.
        Return the definition. Otherwise raise a DefinitionNotInContext
        error. If the context is not present, raise a ContextNotPresent error.
        """

    @abc.abstractmethod
    def definitions(
        self, ctx: BaseInputSetContext
    ) -> BaseDefinitionSetContext:
        """
        Return a DefinitionSet context that can be used to access the inputs
        within the given context, by definition.
        """

    @abc.abstractmethod
    async def gather_inputs(
        self,
        rctx: "BaseRedundancyCheckerContext",
        operation: Operation,
        ctx: Optional[BaseInputSetContext] = None,
    ) -> AsyncIterator[BaseParameterSet]:
        """
        Generate all possible permutations of applicable inputs for an operation
        that, according to the redundancy checker, haven't been run yet.
        """


@base_entry_point("dffml.input.network", "input", "network")
class BaseInputNetwork(BaseDataFlowObject):
    """
    Input networks store all of the input data and output data of operations,
    which in turn becomes input data to other operations.
    """


@config
class LoadSourceInputNetworkConfig:
    pass


class LoadSourceInputNetworkContextEntry(NamedTuple):
    ctx: BaseInputSetContext
    definitions: Dict[Definition, List[Input]]
    by_origin: Dict[Union[str, Tuple[str, str]], List[Input]]


class MemoryDefinitionSetContext(BaseDefinitionSetContext):
    async def inputs(self, definition: Definition) -> AsyncIterator[Input]:
        # Grab the input set context handle
        handle = await self.ctx.handle()
        handle_string = handle.as_string()
        # Associate inputs with their context handle grouped by definition
        async with self.parent.ctxhd_lock:
            # Yield all items under the context for the given definition
            entry = self.parent.ctxhd[handle_string]
            for item in entry.definitions[definition]:
                yield item


class LoadSourceInputNetworkContext(BaseInputNetworkContext):
    def __init__(
        self, config: BaseConfig, parent: "LoadSourceInputNetwork"
    ) -> None:
        super().__init__(config, parent)
        self.ctx_notification_set = NotificationSet()
        self.input_notification_set = {}
        # Organize by context handle string then by definition within that
        self.ctxhd: Dict[str, Dict[Definition, Any]] = {}
        # TODO Create ctxhd_locks dict to manage a per context lock
        self.ctxhd_lock = asyncio.Lock()

    async def receive_from_parent_flow(self, inputs: List[Input]):
        """
        Takes input from parent dataflow and adds it to every active context
        """
        if not inputs:
            return
        async with self.ctxhd_lock:
            ctx_keys = list(self.ctxhd.keys())
        self.logger.debug(f"Receiving {inputs} from parent flow")
        self.logger.debug(f"Forwarding inputs to contexts {ctx_keys}")
        for ctx in ctx_keys:
            await self.sadd(ctx, *inputs)

    async def add(self, input_set: BaseInputSet):
        # Grab the input set context handle
        handle = await input_set.ctx.handle()
        handle_string = handle.as_string()
        # TODO These ctx.add calls should probably happen after inputs are in
        # self.ctxhd

        # remove unvalidated inputs
        unvalidated_input_set = await input_set.remove_unvalidated_inputs()

        # If the context for this input set does not exist create a
        # NotificationSet for it to notify the orchestrator
        if not handle_string in self.input_notification_set:
            self.input_notification_set[handle_string] = NotificationSet()
            async with self.ctx_notification_set() as ctx:
                await ctx.add((None, input_set.ctx))
        # Add the input set to the incoming inputs
        async with self.input_notification_set[handle_string]() as ctx:
            await ctx.add((unvalidated_input_set, input_set))
        # Associate inputs with their context handle grouped by definition
        async with self.ctxhd_lock:
            # Create dict for handle_string if not present
            if not handle_string in self.ctxhd:
                self.ctxhd[handle_string] = LoadSourceInputNetworkContextEntry(
                    ctx=input_set.ctx, definitions={}, by_origin={}
                )
            # Go through each item in the input set
            async for item in input_set.inputs():
                # Create set for item definition if not present
                if (
                    not item.definition
                    in self.ctxhd[handle_string].definitions
                ):
                    self.ctxhd[handle_string].definitions[item.definition] = []
                # Add input to by definition set
                self.ctxhd[handle_string].definitions[item.definition].append(
                    item
                )
                # Create set for item origin if not present
                if not item.origin in self.ctxhd[handle_string].by_origin:
                    self.ctxhd[handle_string].by_origin[item.origin] = []
                # Add input to by origin set
                self.ctxhd[handle_string].by_origin[item.origin].append(item)

    async def uadd(self, *args: Input):
        """
        Shorthand for creating a MemoryInputSet with a StringInputSetContext
        containing a random value for the string.
        """
        # TODO(security) Allow for tuning nbytes
        return await self.sadd(secrets.token_hex(), *args)

    async def sadd(self, context_handle_string, *args: Input):
        """
        Shorthand for creating a MemoryInputSet with a StringInputSetContext.

        >>> import asyncio
        >>> from dffml import *
        >>>
        >>> async def main():
        ...     async with MemoryOrchestrator() as orchestrator:
        ...         async with orchestrator(DataFlow.auto()) as octx:
        ...             await octx.ictx.sadd("Hi")
        >>>
        >>> asyncio.run(main())
        """
        ctx = StringInputSetContext(context_handle_string)
        await self.add(
            MemoryInputSet(MemoryInputSetConfig(ctx=ctx, inputs=list(args)))
        )
        return ctx

    async def cadd(self, ctx, *args: Input):
        """
        Shorthand for creating a MemoryInputSet with an existing context.

        >>> import asyncio
        >>> from dffml import *
        >>>
        >>> async def main():
        ...     async with MemoryOrchestrator() as orchestrator:
        ...         async with orchestrator(DataFlow.auto()) as octx:
        ...             await octx.ictx.sadd(StringInputSetContext("Hi"))
        >>>
        >>> asyncio.run(main())
        """
        await self.add(
            MemoryInputSet(MemoryInputSetConfig(ctx=ctx, inputs=list(args)))
        )
        return ctx

    async def ctx(self) -> Tuple[bool, BaseInputSetContext]:
        async with self.ctx_notification_set() as ctx:
            return await ctx.added()

    async def added(
        self, watch_ctx: BaseInputSetContext
    ) -> Tuple[bool, BaseInputSet]:
        # Grab the input set context handle
        handle_string = (await watch_ctx.handle()).as_string()
        # Notify whatever is listening for new inputs in this context
        async with self.input_notification_set[handle_string]() as ctx:
            """
            return await ctx.added()
            """
            async with ctx.parent.event_added_lock:
                await ctx.parent.event_added.wait()
                ctx.parent.event_added.clear()
                async with ctx.parent.lock:
                    notification_items = ctx.parent.notification_items
                    ctx.parent.notification_items = []
                    return False, notification_items

    async def definition(
        self, ctx: BaseInputSetContext, definition: str
    ) -> Definition:
        async with self.ctxhd_lock:
            # Grab the input set context handle
            handle_string = (await ctx.handle()).as_string()
            # Ensure that the handle_string is present in ctxhd
            if not handle_string in self.ctxhd:
                raise ContextNotPresent(handle_string)
            # Search through the definitions to find one with a matching name
            found = list(
                filter(
                    lambda check: check.name == definition,
                    self.ctxhd[handle_string].definitions,
                )
            )
            # Raise an error if the definition was not found in given context
            if not found:
                raise DefinitionNotInContext(
                    "%s: %s" % (handle_string, definition)
                )
            # If found then return the definition
            return found[0]

    def definitions(
        self, ctx: BaseInputSetContext
    ) -> BaseDefinitionSetContext:
        return MemoryDefinitionSetContext(self.config, self, ctx)

    async def check_conditions(
        self,
        operation: Operation,
        dataflow: DataFlow,
        ctx: BaseInputSetContext,
    ) -> bool:
        async with self.ctxhd_lock:
            # Grab the input set context handle
            handle_string = (await ctx.handle()).as_string()
            # Ensure that the handle_string is present in ctxhd
            if not handle_string in self.ctxhd:
                return
            # Limit search to given context via context handle
            return await self._check_conditions(
                operation, dataflow, self.ctxhd[handle_string].by_origin
            )

    async def _check_conditions(
        self,
        operation: Operation,
        dataflow: DataFlow,
        by_origin: Dict[Union[str, Tuple[str, str]], List[Input]],
    ) -> bool:
        # Grab the input flow to check for definition overrides
        input_flow = dataflow.flow[operation.instance_name]
        # Return that all conditions are satisfied if there are none to satisfy
        if not input_flow.conditions:
            return True
        # Check that all conditions are present and logicly True
        for i, condition_source in enumerate(input_flow.conditions):
            # We must check if we found an Input where the definition
            # matches the definition of the condition in addition to
            # checking that the Input's value is True. If we were not
            # to check that we found a definition we would be effectively
            # saying that the lack of presence equates with the
            # condition being True.
            condition_found_and_true = False
            # Create a list of places this input originates from
            origins = []
            if isinstance(condition_source, dict):
                for origin in condition_source.items():
                    origins.append(origin)
            else:
                origins.append(condition_source)
            # Ensure all conditions from all origins are True
            for origin in origins:
                # See comment in input_flow.inputs section
                (
                    alternate_definitions,
                    origin,
                ) = input_flow.get_alternate_definitions(origin)
                # Bail if the condition doesn't exist
                if not origin in by_origin:
                    return
                # Bail if the condition is not True
                for item in by_origin[origin]:
                    # TODO(p2) Alright, this shits fucked, way not clean
                    # / clear. We're just trying to skip any conditions
                    # (and inputs for input_flow.inputs.items()) where
                    # the definition doesn't match, but it's within the
                    # correct origin.
                    if alternate_definitions:
                        if item.definition.name not in alternate_definitions:
                            continue
                    elif isinstance(condition_source, str):
                        if (
                            item.definition.name
                            != operation.conditions[i].name
                        ):
                            continue
                    elif (
                        item.definition.name
                        != dataflow.operations[origin[0]]
                        .outputs[origin[1]]
                        .name
                    ):
                        continue
                    condition_found_and_true = bool(item.value)
            # Ensure we were able to find a condition within the input
            # network, and that when we found it it's value was True.
            if condition_found_and_true:
                return True
        return False

    async def gather_inputs(
        self,
        rctx: "BaseRedundancyCheckerContext",
        operation: Operation,
        dataflow: DataFlow,
        ctx: Optional[BaseInputSetContext] = None,
    ) -> AsyncIterator[BaseParameterSet]:
        # Create a mapping of definitions to inputs for that definition
        gather: Dict[str, List[Parameter]] = {}
        async with self.ctxhd_lock:
            # If no context is given we will generate input pairs for all
            # contexts
            contexts = self.ctxhd.values()
            # If a context is given only search definitions within that context
            if not ctx is None:
                # Grab the input set context handle
                handle_string = (await ctx.handle()).as_string()
                # Ensure that the handle_string is present in ctxhd
                if not handle_string in self.ctxhd:
                    return
                # Limit search to given context via context handle
                contexts = [self.ctxhd[handle_string]]
            for ctx, _, by_origin in contexts:
                # Ensure we were able to find a condition within the input
                # network, and that when we found it it's value was True.
                if not await self._check_conditions(
                    operation, dataflow, by_origin
                ):
                    return
                # Grab the input flow to check for definition overrides
                input_flow = dataflow.flow[operation.instance_name]
                # Gather all inputs with matching definitions and contexts
                for input_name, input_sources in input_flow.inputs.items():
                    # Create parameters for all the inputs
                    gather[input_name] = []
                    for input_source in input_sources:
                        # Create a list of places this input originates from
                        origins = []
                        # Handle the case where we look at the first instance in
                        # the list for the immediate alternate definition then
                        # trace back through input origins to make sure they all
                        # match
                        if isinstance(input_source, list):
                            # TODO Refactor this since we have duplicate code
                            if isinstance(input_source[0], dict):
                                for origin in input_source[0].items():
                                    origins.append(origin)
                            else:
                                origins.append(input_source[0])
                        elif isinstance(input_source, dict):
                            for origin in input_source.items():
                                origins.append(origin)
                        else:
                            origins.append(input_source)
                        for origin in origins:
                            # Check if the origin is a tuple where the first
                            # value is the origin (such as "seed") and the
                            # second value is an array of allowed alternate
                            # Definition's (their names) within that origin.
                            # These definitions will be used instead of the
                            # default one the input specified for the
                            # operation).
                            (
                                alternate_definitions,
                                origin,
                            ) = input_flow.get_alternate_definitions(origin)
                            # Don't try to grab inputs from an origin that
                            # doesn't have any to give us
                            if not origin in by_origin:
                                continue
                            # Generate parameters from inputs
                            for item in by_origin[origin]:
                                # TODO(p2) We favored comparing names to
                                # definitions because sometimes we create
                                # definitions which have specs which create new
                                # types which will not equal each other. We
                                # maybe want to consider switching to comparing
                                # exported Definitions
                                if alternate_definitions:
                                    if (
                                        item.definition.name
                                        not in alternate_definitions
                                    ):
                                        continue
                                elif isinstance(origin, str):
                                    if (
                                        item.definition.name
                                        != operation.inputs[input_name].name
                                    ):
                                        continue
                                elif (
                                    item.definition.name
                                    != dataflow.operations[origin[0]]
                                    .outputs[origin[1]]
                                    .name
                                ):
                                    continue
                                # When the input_source is a list of alternate
                                # definitions we need to check each parent to
                                # verity that it's origin matches with the list
                                # given by input_source
                                if isinstance(input_source, list):
                                    all_parent_origins_match = True
                                    # Make a list of all the origins
                                    ancestor_origins = []
                                    for ancestor_origin in input_source:
                                        if isinstance(ancestor_origin, dict):
                                            for (
                                                ancestor_origin
                                            ) in ancestor_origin.items():
                                                ancestor_origins.append(
                                                    ancestor_origin
                                                )
                                        else:
                                            ancestor_origins.append(
                                                ancestor_origin
                                            )
                                    i = 1
                                    current_parent = item
                                    while i < len(ancestor_origins):
                                        ancestor_origin = ancestor_origins[i]
                                        # Go through all the parents. Create a
                                        # list of possible parents based on if
                                        # their origin matches the alternate
                                        # definition
                                        possible_parents = [
                                            parent
                                            for parent in current_parent.parents
                                            # If the input source is a dict then
                                            # we need to convert it to a tuple
                                            # for comparison to the origin
                                            if parent.origin == ancestor_origin
                                        ]
                                        if not possible_parents:
                                            all_parent_origins_match = False
                                            break
                                        elif len(possible_parents) > 1:
                                            # TODO Go through each option and
                                            # check if either is a viable
                                            # option. Our current implementation
                                            # only allows for valeting one path,
                                            # due to a single current_parent
                                            # If there is more than one option
                                            # raise an error since we don't know
                                            # who to choose
                                            raise MultipleAncestorsFoundError(
                                                (
                                                    operation.instance_name,
                                                    input_name,
                                                    ancestor_origin,
                                                    [
                                                        parent.__dict__
                                                        for parent in possible_parents
                                                    ],
                                                )
                                            )
                                        # Move on to the next origin to validate
                                        i += 1
                                        # The current_parent becomes the only
                                        # possible parent
                                        current_parent = possible_parents[0]
                                    # If we didn't find any ancestor paths that
                                    # matched then we don't use this Input
                                    if not all_parent_origins_match:
                                        continue
                                gather[input_name].append(
                                    Parameter(
                                        key=input_name,
                                        value=item.value,
                                        origin=item,
                                        definition=operation.inputs[
                                            input_name
                                        ],
                                    )
                                )
                    # There is no data in the network for an input
                    if not gather[input_name]:
                        # Check if there is a default value for the parameter,
                        # if so use it. That default will either come from the
                        # definition attached to input_name, or it will come
                        # from one of the alternate definition given within the
                        # input flow for the input_name.
                        check_for_default_value = [
                            operation.inputs[input_name]
                        ] + alternate_definitions
                        for definition in check_for_default_value:
                            # Check if the definition has a default value that is not _NO_DEFAULT
                            if "dffml.df.types._NO_DEFAULT" not in repr(
                                definition.default
                            ):
                                gather[input_name].append(
                                    Parameter(
                                        key=input_name,
                                        value=definition.default,
                                        origin=item,
                                        definition=operation.inputs[
                                            input_name
                                        ],
                                    )
                                )
                                break
                        # If there is no default value, we don't have a complete
                        # parameter set, so we bail out
                        else:
                            return
        # Generate all possible permutations of applicable inputs
        # Create the parameter set for each
        products = list(
            map(
                lambda permutation: MemoryParameterSet(
                    MemoryParameterSetConfig(ctx=ctx, parameters=permutation)
                ),
                product(*list(gather.values())),
            )
        )
        # Check if each permutation has been executed before
        async for parameter_set, taken in rctx.take_if_non_existant(
            operation, *products
        ):
            # If taken then yield the permutation
            if taken:
                yield parameter_set


@entrypoint("source.load")
class LoadSourceInputNetwork(BaseInputNetwork, BaseMemoryDataFlowObject):
    """
    Load an input network with data from from underlying source on initial load.

    .. code-block:: console
        :test:
    """

    CONTEXT = LoadSourceInputNetworkContext
    CONFIG = LoadSourceInputNetworkConfig


class OperationImplementationNotInstantiable(Exception):
    """
    OperationImplementation cannot be instantiated and is required to continue.
    """


class OperationImplementationNotInstantiated(Exception):
    """
    OperationImplementation is instantiable, but is not has not been
    instantiated within the network and was required to continue.

    Attempted to run operation which could be instantiated, but has not yet
    been.
    """


class BaseOperationNetworkContext(BaseDataFlowObjectContext):
    """
    Abstract Base Class for context managing operations
    """

    @abc.abstractmethod
    async def add(self, operations: List[Operation]):
        """
        Add operations to the network
        """

    @abc.abstractmethod
    async def operations(
        self, input_set: BaseInputSet = None, stage: Stage = Stage.PROCESSING
    ) -> AsyncIterator[Operation]:
        """
        Retrieve all operations in the network of a given stage filtering by
        operations who have inputs with definitions in the input set.
        """


# TODO Make this operate like a BaseInputNetwork were operations can
# be added dynamically
@base_entry_point("dffml.operation.network", "operation", "network")
class BaseOperationNetwork(BaseDataFlowObject):
    """
    Operation networks hold Operation objects to allow for looking up of their
    inputs, outputs, and conditions.
    """


class BaseRedundancyCheckerConfig(NamedTuple):
    key_value_store: BaseKeyValueStore


# TODO store redundancy checks by BaseInputSetContext.handle() and add method
# to remove all associated with a particular handle. Aka allow us to clean up
# the input, redundancy, etc. networks after execution of a context completes
# via the orchestrator.
class BaseRedundancyCheckerContext(BaseDataFlowObjectContext):
    """
    Abstract Base Class for redundancy checking context
    """

    @abc.abstractmethod
    async def exists(
        self, operation: Operation, parameter_set: BaseParameterSet
    ) -> bool:
        pass

    @abc.abstractmethod
    async def add(self, operation: Operation, parameter_set: BaseParameterSet):
        pass


@base_entry_point("dffml.redundancy.checker", "rchecker")
class BaseRedundancyChecker(BaseDataFlowObject):
    """
    Redundancy Checkers ensure that each operation within a context only gets
    run with a give permutation of inputs once.
    """


# TODO Provide a way to clear out all locks for inputs within a context
class BaseLockNetworkContext(BaseDataFlowObjectContext):
    @abc.abstractmethod
    async def acquire(self, parameter_set: BaseParameterSet) -> bool:
        """
        An async context manager which will acquire locks of all inputs within
        the parameter set.
        """


@base_entry_point("dffml.lock.network", "lock", "network")
class BaseLockNetwork(BaseDataFlowObject):
    """
    Acquires locks on inputs which may not be used simultaneously
    """


class BaseOperationImplementationNetworkContext(BaseDataFlowObjectContext):
    @abc.abstractmethod
    async def contains(self, operation: Operation) -> bool:
        """
        Checks if the network contains / has the ability to run a given
        operation.
        """

    @abc.abstractmethod
    async def instantiable(self, operation: Operation) -> bool:
        """
        Prior to figuring out which operation implementation networks contain
        an operation, if none do, they will need to instantiate it on the fly.
        """

    @abc.abstractmethod
    async def instantiate(
        self, operation: Operation, config: BaseConfig
    ) -> bool:
        """
        Instantiate a given operation so that it can be run within this network.
        """

    @abc.abstractmethod
    async def run(
        self, operation: Operation, inputs: Dict[str, Any]
    ) -> Union[bool, Dict[str, Any]]:
        """
        Find the operation implementation for the given operation and create an
        operation implementation context, call the run method of the context and
        return the results.
        """

    @abc.abstractmethod
    async def operation_completed(self):
        """
        Returns when an operation finishes
        """

    @abc.abstractmethod
    async def dispatch(
        self,
        ictx: BaseInputNetworkContext,
        lctx: BaseLockNetworkContext,
        operation: Operation,
        parameter_set: BaseParameterSet,
    ):
        """
        Schedule the running of an operation
        """


# TODO We should be able to specify multiple operation implementation  networks.
# This would enable operations to live in different place, accessed via the
# orchestrator transparently. This will probably involve
# dffml.util.asynchelper.AsyncContextManagerList
@base_entry_point("dffml.operation.implementation.network", "opimp", "network")
class BaseOperationImplementationNetwork(BaseDataFlowObject):
    """
    Knows where operations are or if they can be made
    """


class OperationException(Exception):
    """
    Raised by the orchestrator when an operation throws an exception.
    """


@dataclass(frozen=True)
class BaseOrchestratorConfig:
    input_network: BaseInputNetwork
    operation_network: BaseOperationNetwork
    lock_network: BaseLockNetwork
    opimp_network: BaseOperationImplementationNetwork
    rchecker: BaseRedundancyChecker

    def _replace(self, **kwargs):
        return replace(self, **kwargs)


class BaseOrchestratorContext(BaseDataFlowObjectContext):
    @abc.abstractmethod
    async def run_operations(
        self, strict: bool = True
    ) -> AsyncIterator[Tuple[BaseContextHandle, Dict[str, Any]]]:
        """
        Run all the operations then run cleanup and output operations
        """

    @abc.abstractmethod
    async def operations_parameter_set_pairs(
        self,
        ctx: BaseInputSetContext,
        *,
        new_input_set: BaseInputSet = None,
        stage: Stage = Stage.PROCESSING,
    ) -> AsyncIterator[Tuple[Operation, BaseParameterSet]]:
        """
        Use new_input_set to determine which operations in the network might be
        up for running. Cross check using existing inputs to generate per
        input set context novel input pairings. Yield novel input pairings
        along with their operations as they are generated.
        """


@base_entry_point("dffml.orchestrator", "orchestrator")
class BaseOrchestrator(BaseDataFlowObject):
    @classmethod
    async def run(cls, dataflow, inputs, *, config=None, **kwargs):
        if config is None:
            self = cls.withconfig({})
        else:
            self = cls(config=config, **kwargs)
        async with self as orchestrator:
            async with orchestrator(dataflow) as octx:
                async for ctx, results in octx.run(inputs):
                    yield ctx, results
