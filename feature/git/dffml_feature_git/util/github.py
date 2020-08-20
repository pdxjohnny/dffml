"""
GitHub API Helper
"""
import keyring
import aiohttp
import datetime
from typing import Dict, Any

from dffml import (
    config,
    field,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)

GRAPHQL_REQUEST_BODY = """
      totalCount
      edges {
        node {
          title
          createdAt
          closedAt
          labels(first: 100) {
            nodes {
              name
              description
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
"""
GRAPHQL_REQUEST_FIRST = (
    """{
  repository(owner: "%s", name: "%s") {
    %s(first: 100) {
    """
    + GRAPHQL_REQUEST_BODY
    + """
    }
  }
}"""
)
GRAPHQL_REQUEST_PAGE = (
    """{
  repository(owner: "%s", name: "%s") {
    %s(first: 100, after: "%s") {
    """
    + GRAPHQL_REQUEST_BODY
    + """
    }
  }
}"""
)


class GitHubRepoNotFound(Exception):
    pass


class FromDict(object):
    def __init__(self, data: Dict[str, Any]):
        for key, value in data.items():
            if not key.startswith("__") and not key.startswith("_"):
                convert = getattr(self, "_convert_" + key, False)
                if convert:
                    value = convert(value)
                setattr(self, key, value)

    def _convert_createdAt(self, value):
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")

    def _convert_labels(self, value):
        return dict(
            map(
                lambda label: (label["name"], label["description"]),
                list(value.values())[0],
            )
        )

    def __repr__(self):
        return "%s: %s" % (
            self.__class__.__qualname__,
            {
                key: getattr(self, key)
                for key in self.__dir__()
                if not key.startswith("_")
            },
        )


class GitHubIssue(FromDict):
    pass


class GitHubPullRequest(FromDict):
    pass


@config
class GitHubConfig:
    token: str = field("GitHub API token")


class GitHubContext(BaseDataFlowFacilitatorObjectContext):
    ENDPOINT: str = "https://api.github.com/graphql"

    def __init__(self, parent: "GitHub"):
        super().__init__()
        self.parent = parent

    @classmethod
    def _gql_first(cls, request: str, owner: str, project: str) -> str:
        return GRAPHQL_REQUEST_FIRST % (owner, project, request)

    @classmethod
    def _gql_page(
        cls, request: str, owner: str, project: str, cursor: str
    ) -> str:
        return GRAPHQL_REQUEST_PAGE % (owner, project, request, cursor)

    @classmethod
    def _gql_issues_first(cls, *args) -> str:
        return cls._gql_first("issues", *args)

    @classmethod
    def _gql_pull_requests_first(cls, *args) -> str:
        return cls._gql_first("pullRequests", *args)

    @classmethod
    def _gql_issues_page(cls, *args) -> str:
        return cls._gql_page("issues", *args)

    @classmethod
    def _gql_pull_requests_page(cls, *args) -> str:
        return cls._gql_page("pullRequests", *args)

    @staticmethod
    def ensure_member(data, key):
        if not key in data:
            raise ValueError("No %r in: %r" % (key, data))
        return data[key]

    async def _pager(
        self, name: str, owner: str, project: str, first, page, dType
    ) -> str:
        num: int = 0
        totalCount: int = -1
        req = first(owner, project)
        self.logger.debug(
            "%s: sending graphql request: %s",
            self.__class__.__qualname__,
            req,
        )
        nextPage = True
        while nextPage:
            async with self.parent.session.post(
                self.ENDPOINT, json={"query": req}
            ) as resp:
                resp_json = await resp.json()
                data = self.ensure_member(resp_json, "data")
                if data is None:
                    errors = self.ensure_member(resp_json, "errors")
                    raise Exception(errors)
                repo = self.ensure_member(data, "repository")
                internals = self.ensure_member(repo, name)
                totalCount = self.ensure_member(internals, "totalCount")
                edges = self.ensure_member(internals, "edges")
                pageInfo = self.ensure_member(internals, "pageInfo")
                endCursor = self.ensure_member(pageInfo, "endCursor")
                nextPage = self.ensure_member(pageInfo, "hasNextPage")
                for internal in edges:
                    node = self.ensure_member(internal, "node")
                    num += 1
                    yield dType(node)
                req = page(owner, project, endCursor)
                self.logger.debug(
                    "%s: sending graphql request: %s",
                    self.__class__.__qualname__,
                    req,
                )
        if totalCount != num:
            raise ValueError(
                "Should have received %d repos but got %d" % (totalCount, num)
            )

    async def issues(self, owner: str, project: str) -> str:
        async for issue in self._pager(
            "issues",
            owner,
            project,
            self._gql_issues_first,
            self._gql_issues_page,
            GitHubIssue,
        ):
            yield issue

    async def pull_requests(self, owner: str, project: str) -> str:
        async for pull_req in self._pager(
            "pullRequests",
            owner,
            project,
            self._gql_pull_requests_first,
            self._gql_pull_requests_page,
            GitHubPullRequest,
        ):
            yield pull_req


class GitHub(BaseDataFlowFacilitatorObject):
    CONFIG = GitHubConfig
    CONTEXT = GitHubContext

    def __call__(self):
        return self.CONTEXT(self)

    @staticmethod
    def owner_project(url: str):
        """
        Parses the owner and project name out of a GitHub URL

        Examples
        --------

        >>> GitHub.owner_project("https://github.com/intel/dffml")
        ('intel', 'dffml')
        """
        return tuple("/".join(url.split("/")[-2:]).split("/"))

    async def __aenter__(self):
        self.headers = {"Authorization": "bearer %s" % (self.config.token)}
        self.session = aiohttp.ClientSession(
            trust_env=True, headers=self.headers
        )
        await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.__aexit__(exc_type, exc_value, traceback)
