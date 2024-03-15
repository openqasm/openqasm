import re
import logging

import sphinx
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_id, make_refnode

_LOG = logging.getLogger(__name__)


class OpenQASMGate(ObjectDescription):
    # Parsing code through superset regexes - good enough for docs, where we can assume there
    # weren't any syntax errors.
    SIGNATURE = re.compile(
        r"(?P<name>\w+)\s*(\((?P<params>(\s*\w+,?)*)\))?(?P<qubits>(\s*\w+,?)*)",
        flags=re.U,
    )

    def _object_hierarchy_parts(self, sig_node):
        return (sig_node["name"],)

    def _toc_entry_node(self, sig_node):
        return sig_node["name"]

    def add_target_and_index(self, name, sig: str, signode):
        node_id = make_id(self.env, self.state.document, "", name)
        signode["ids"].append(node_id)
        domain = self.env.domains["oq"]
        domain.index_object(name, "gate", node_id)
        self.indexnode["entries"].append(("single", name, node_id, "", None))

    def handle_signature(self, sig: str, signode):
        if (m := self.SIGNATURE.match(sig)) is None:
            raise ValueError(f"bad gate signature: '{sig}'")
        name = m["name"]
        params = (
            [param.strip() for param in m["params"].split(",")]
            if m["params"] is not None
            else []
        )
        qubits = [qubit.strip() for qubit in m["qubits"].split(",")]

        # This isn't perfect (there's semantics missing), but good enough for proof-of-concept.
        signode["name"] = name
        signode += addnodes.desc_sig_keyword_type(text="gate")
        signode += addnodes.desc_sig_space()
        signode += addnodes.desc_name(name, name)
        if params:
            params_node = addnodes.desc_parameterlist(m["params"])
            for param in params:
                param_node = addnodes.desc_parameter()
                param_node += addnodes.desc_sig_name("", param)
                params_node += param_node
            signode += params_node
        for qubit in qubits:
            signode += addnodes.desc_sig_space()
            qubit_node = addnodes.desc_sig_name()
            qubit_node += addnodes.desc_sig_name("", qubit)
            signode += qubit_node
        return name


class QASMDomain(Domain):
    """OpenQASM language domain."""

    name = "oq"
    label = "OpenQASM"
    object_types = {
        "gate": ObjType("gate", "gate"),
    }
    directives = {
        "gate": OpenQASMGate,
    }
    roles = {
        "gate": XRefRole(),
    }
    initial_data = {
        "objects": {},
    }

    def index_object(self, name: str, objtype: str, node_id: str):
        if name in self.data["objects"]:
            _LOG.warning("duplicate entry for '%s'", name)
            return
        self.data["objects"][name] = (self.env.docname, node_id, objtype)

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        if (lookup := self.data["objects"].get(target)) is None:
            return None
        name, node_id, objtype = lookup
        if objtype != typ:
            return None
        return make_refnode(builder, fromdocname, name, node_id, [contnode], name)


# Setup a basic Sphinx domain for documenting OpenQASM programs.

def setup(app):
    app.add_domain(QASMDomain)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
