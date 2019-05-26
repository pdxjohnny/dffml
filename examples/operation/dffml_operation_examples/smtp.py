import smtplib
import asyncio
from typing import NamedTuple, Dict, Any

from dffml.base import BaseConfig
from dffml.df.types import Definition, Operation
from dffml.df.base import OperationImplementationContext, \
                          OperationImplementation
from dffml.util.cli.arg import Arg

send_email_spec = Definition(
    name='send_email_spec',
    primitive='Dict[str, str]')

insecure_smtp = Operation(
    name='insecure_smtp',
    inputs={
        'spec': send_email_spec
        },
    outputs={},
    conditions=[])

class InsecureSMTPConfig(BaseConfig, NamedTuple):
    host: str
    port: int
    email: str
    password: str

class InsecureSMTPContext(OperationImplementationContext):

    op = insecure_smtp

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        spec = inputs['spec']
        async with self.parent.lock:
            self.parent.send(spec['to'], spec['subject'], spec['content'])

# TODO smtplib.SMTP should live in a thread, since we can't bind it's socket to
# the event loop.
class InsecureSMTP(OperationImplementation):

    op = insecure_smtp
    CONTEXT = InsecureSMTPContext

    def __init__(self, config):
        super().__init__(config)
        self.lock = None
        self.session = None
        self.logger.critical('DANGER: Insecure SMTP connection in use')

    async def __aenter__(self):
        self.lock = asyncio.Lock()
        self.session = smtplib.SMTP(self.config.host, self.config.port)
        self.session.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.session.__exit__(None, None, None)

    def send(self, to, subject, content):
        headers = "\r\n".join(["from: " + self.config.email,
            "subject: " + subject,
            "to: " + to,
            "mime-version: 1.0",
            "content-type: text/plain"])
        content = headers + "\r\n\r\n" + content
        self.session.sendmail(self.config.email, to, content)

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(args, above, 'host', Arg())
        cls.config_set(args, above, 'port',
                Arg(type=int, default=25))
        cls.config_set(args, above, 'email', Arg())
        cls.config_set(args, above, 'password', Arg())
        return args

    @classmethod
    def config(cls, config, *above):
        return InsecureSMTPConfig(
            host=cls.config_get(config, above, 'host'),
            port=cls.config_get(config, above, 'port'),
            email=cls.config_get(config, above, 'email'),
            password=cls.config_get(config, above, 'password')
            )
