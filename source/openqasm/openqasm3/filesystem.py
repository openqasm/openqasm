"""
==========================================================
File-system include resolution (``openqasm3.filesystem``)
==========================================================

An opt-in :class:`~openqasm3.resolver.IncludeResolver` that loads source units from disk.

This is the only module in the package that touches the file system.  It is never used unless a
caller explicitly constructs it and passes it to the parser, because an include target may
originate from untrusted source text.

.. currentmodule:: openqasm3.filesystem
.. autoclass:: FileSystemResolver
"""

__all__ = ["FileSystemResolver"]

import os
from typing import Iterable, List, Optional, Union

from .resolver import IncludeError, IncludeResolver, ResolvedSource, candidate_names


class FileSystemResolver(IncludeResolver):
    """Resolves include targets against an explicit list of search roots.

    :param search_path: Directories to search, in order.  A candidate name is only accepted if the
        file it names lies inside the root being searched, so an include target cannot reach
        outside the roots the caller designated.
    :param encoding: Text encoding used to read source files.

    Canonical names are the candidate name that matched, joined to the matching root, expressed
    with forward slashes.  Two roots that reach the same file through different names produce two
    canonical names and therefore two source units; the specification makes no promise about
    physical file identity.
    """

    def __init__(self, search_path: Iterable[Union[str, os.PathLike]], encoding: str = "utf-8"):
        self._search_path: List[str] = [os.path.abspath(os.fspath(root)) for root in search_path]
        self._encoding = encoding
        if not self._search_path:
            raise ValueError("FileSystemResolver requires at least one search root")

    def resolve(self, target: str, includer: str) -> Optional[ResolvedSource]:
        for candidate in candidate_names(target, includer):
            for root in self._search_path:
                path = os.path.abspath(os.path.join(root, candidate))
                if os.path.commonpath([root, path]) != root:
                    # The candidate escapes the designated root, so this root does not supply it.
                    continue
                if not os.path.isfile(path):
                    continue
                try:
                    with open(path, "r", encoding=self._encoding) as stream:
                        return ResolvedSource(stream.read(), candidate.replace("\\", "/"))
                except OSError as exc:
                    raise IncludeError(
                        f"could not read '{path}' for include target '{target}': {exc}"
                    ) from exc
        return None

    def __repr__(self):
        return f"{type(self).__name__}({self._search_path!r})"
