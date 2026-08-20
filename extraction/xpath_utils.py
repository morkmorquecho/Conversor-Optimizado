"""
Traduce paths en notación Clark ({namespace}tag) — como los que genera
Diverza — a una expresión XPath real ejecutable con lxml, que sí requiere
prefijos declarados en un namespace map en vez de URIs embebidas.

Ejemplo de entrada:
//{http://www.sat.gob.mx/cfd/4}Addenda/{http://www.diverza.com/ns/addenda/diverza/1}diverza/
  {http://www.diverza.com/ns/addenda/diverza/1}complemento/
  {http://www.diverza.com/ns/addenda/diverza/1}datosExtra[@atributo='LeyendaEspecial31']/@valor
"""
import re
from typing import Optional
from lxml import etree

_CLARK_RE = re.compile(r"\{[^}]*\}")


def _split_path(path: str) -> list[str]:
    """Separa por '/' ignorando las '/' que quedan dentro de {uri}."""
    segments, current, depth = [], [], 0
    for ch in path:
        if ch == "{":
            depth += 1
            current.append(ch)
        elif ch == "}":
            depth -= 1
            current.append(ch)
        elif ch == "/" and depth == 0:
            segments.append("".join(current))
            current = []
        else:
            current.append(ch)
    if current:
        segments.append("".join(current))
    return segments


def clark_path_to_xpath(path: str) -> tuple[str, dict]:
    path = path.strip()
    head = ""
    if path.startswith("//"):
        head, path = "//", path[2:]
    elif path.startswith("/"):
        head, path = "/", path[1:]

    namespaces: dict[str, str] = {}
    out = []
    for segment in (s for s in _split_path(path) if s):
        match = _CLARK_RE.match(segment)
        if not match:
            out.append(segment)  # ej: '@valor', o un segmento sin namespace
            continue
        uri = match.group(0)[1:-1]
        rest = segment[match.end():]
        prefix = next((p for p, u in namespaces.items() if u == uri), None)
        if prefix is None:
            prefix = f"ns{len(namespaces)}"
            namespaces[prefix] = uri
        out.append(f"@{prefix}:{rest[1:]}" if rest.startswith("@") else f"{prefix}:{rest}")

    return head + "/".join(out), namespaces


def resolve_xpath_value(xml_root, path: str) -> Optional[str]:
    """Devuelve el primer match como string, o None si no hay coincidencias."""
    xpath_expr, namespaces = clark_path_to_xpath(path)
    try:
        result = xml_root.xpath(xpath_expr, namespaces=namespaces)
    except etree.XPathEvalError as exc:
        raise ValueError(f"XPath inválido para '{path}' -> '{xpath_expr}': {exc}") from exc
    if not result:
        return None
    value = result[0]
    if isinstance(value, etree._Element):
        return (value.text or "").strip()
    return str(value).strip()