import argparse
import ast
import itertools
import logging
import os

from fhir_py_types.ast import build_ast
from fhir_py_types.reader.bundle import load_from_bundle


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

FHIR_TO_SYSTEM_TYPE_MAP = {
    "System.String": "str",
    "System.Boolean": "bool",
    "System.Time": "str",
    "System.Date": "str",
    "System.DateTime": "str",
    "System.Decimal": "int",
    "System.Integer": "int",
}

def parse_primitive_type_amp(primitive_overrides: list[str]) -> tuple[dict[str, str], list[str]]:
    """Parse the primitive type overrides from the command line and """
    """return a tuple containing (1) a map of FHIR primitive types to Python types, a list of import statements."""
    override_map = dict(arg.split("=") for arg in primitive_overrides)
    if not override_map:
        return FHIR_TO_SYSTEM_TYPE_MAP, []
    module_path_type_list:list[tuple[str, str]] = [tuple(qualified_name.rsplit(".", 1)) for qualified_name in override_map.values()]
    system_type_map = {fhir_type: f"{type_}_" for (_, type_), fhir_type in zip(module_path_type_list, override_map.keys())}
    import_statements = set(f"from {module} import {type_} as {type_}_" for module, type_ in module_path_type_list)
    return { **FHIR_TO_SYSTEM_TYPE_MAP, **system_type_map}, list(import_statements)


def main() -> None:
    argparser = argparse.ArgumentParser(
        description="Generate Python typed data models from FHIR resources definition"
    )
    argparser.add_argument(
        "--from-bundles",
        action="append",
        required=True,
        help="File path to read 'StructureDefinition' resources from (repeat to read multiple files)",
    )
    argparser.add_argument(
        "--outfile",
        required=True,
        help="File path to write generated Python typed data models to",
    )
    argparser.add_argument(
        "--base-model",
        default="pydantic.BaseModel",
        help="Python path to the Base Model class to use as the base class for generated models",
    )
    argparser.add_argument(
        "--primitive",
        action="append",
        default=[],
        help="Override the default mapping of FHIR primitive types to Python types usign the format 'fhir_type=python_type'. "\
             "Each `python_type` must be a PEP 3155 qualified name (e.g. 'datetime.date'). "\
             "Each `fhir_type` must be a FHIRPath System type (e.g. 'System.String')",
    )
    
    args = argparser.parse_args()
    primitive_type_map, import_stmts = parse_primitive_type_amp(args.primitive)
    structure_definitions = itertools.chain.from_iterable(load_from_bundle(bundle, primitive_type_map) for bundle in args.from_bundles)
    ast_ = build_ast(structure_definitions)

    with open(os.path.abspath(args.outfile), "w") as resource_file:
        resource_file.writelines(
            [
                "from typing import List as List_, Optional as Optional_, Literal as Literal_, Annotated as Annotated_, NewType as NewType_\n",
                "\n".join(import_stmts)+"\n",
                "from %s import %s as BaseModel\n" % tuple(args.base_model.rsplit(".", 1)),
                "from pydantic import Field, Extra\n",
                "\n\n",
                "\n\n\n".join(
                    ast.unparse(ast.fix_missing_locations(tree)) for tree in ast_
                ),
            ]
        )
