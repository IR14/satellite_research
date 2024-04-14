from typing import Union, List, Dict

JsonSimpleType = Union[int, float, bool, None, str]
JsonType = Union[JsonSimpleType, List['JSONType'], Dict[str, 'JSONType']]
