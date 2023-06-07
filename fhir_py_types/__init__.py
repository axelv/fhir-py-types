from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Literal


class StructureDefinitionKind(Enum):
    PRIMITIVE = "primitive-type"
    COMPLEX = "complex-type"
    CAPABILITY = "capability"
    OPERATION = "operation"
    RESOURCE = "resource"

    @staticmethod
    def from_str(kind):
        match kind:
            case "primitive-type":
                return StructureDefinitionKind.PRIMITIVE
            case "complex-type":
                return StructureDefinitionKind.COMPLEX
            case "capability":
                return StructureDefinitionKind.CAPABILITY
            case "operation":
                return StructureDefinitionKind.OPERATION
            case "resource":
                return StructureDefinitionKind.RESOURCE
            case _:
                raise ValueError(f"Unknown StructureDefinition kind: {kind}")
class StructureDefinitionDerivation(Enum):
    CONSTRAINT = "constraint"
    SPECIALIZATION = "specialization"

    @staticmethod
    def from_str(derivation: str):
        match derivation:
            case "constraint":
                return StructureDefinitionDerivation.CONSTRAINT
            case "specialization":
                return StructureDefinitionDerivation.SPECIALIZATION
            case _:
                raise ValueError(f"Unknown StructureDefinition derivation: {derivation}")



@dataclass(frozen=True)
class StructurePropertyType:
    code: str
    required: bool = False
    isarray: bool = False
    literal: bool = False
    target_profile: Optional[List[str]] = None


@dataclass(frozen=True)
class StructureDefinition:
    id: str
    docstring: str
    type: List[StructurePropertyType]
    elements: dict[str, "StructureDefinition"]
    choice_type: bool = False
    derivation: StructureDefinitionDerivation | None = None
    abstract: bool = False
    kind: Optional[StructureDefinitionKind] = None

def is_polymorphic(definition: StructureDefinition):
    return definition.choice_type 

def is_resource_profile(definition: StructureDefinition):
    return definition.derivation == StructureDefinitionDerivation.CONSTRAINT and definition.kind == StructureDefinitionKind.RESOURCE

