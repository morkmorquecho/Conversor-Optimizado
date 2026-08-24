"""
Construcción de prompts y JSON Schema para extracción de datos de PDF vía LLM.

Este módulo NO hace la llamada al LLM (eso vive en tu cliente/servicio de
extracción). Solo arma:
  - SYSTEM_PROMPT: fijo, reglas de comportamiento del modelo.
  - build_user_prompt(): dinámico, arma el mensaje de usuario a partir de un
    Template y su texto/tablas ya extraídos por pdfplumber.
  - build_json_schema(): arma el JSON Schema que se fuerza como structured
    output en la llamada al LLM.

Palabras de corte genéricas (fallback cuando un TemplateField de tipo
line_item no define block_end_anchor propio). Viven en código, no en BD,
porque son lógica general del sistema, no configuración por proveedor.
"""

from templates.models import TemplateField  

SYSTEM_PROMPT = """\
Eres un motor de extracción de datos. Tu única función es leer el texto de un
documento y devolver los valores solicitados, exactamente como aparecen en el
texto fuente. No eres un asistente conversacional: no expliques, no comentes,
no agregues texto fuera del JSON de salida.

REGLAS ESTRICTAS:

1. EXTRAE, NO INTERPRETES. Devuelve el valor tal cual aparece en el texto
   fuente (mismo formato, mismos caracteres). No conviertas fechas, no
   reformatees montos, no traduzcas, no corrijas ortografía. La normalización
   del valor la hace un proceso posterior, no tú.

2. CAMPOS CERRADOS. Devuelve únicamente los campos que se te piden
   explícitamente en la lista de campos. Nunca agregues campos adicionales,
   nunca infieras campos que no estén en la lista.

3. SIN INVENTAR. Si un campo de encabezado no se encuentra en el texto, o no
   puedes ubicarlo con certeza usando la referencia (ancla) proporcionada, su
   valor debe ser null. Nunca completes con un valor supuesto, promedio, o
   "el más probable".

4. DESAMBIGUACIÓN. Si un texto ancla aparece más de una vez, usa la
   ocurrencia más cercana al inicio del documento salvo que las
   instrucciones del campo indiquen lo contrario. Si sigue habiendo
   ambigüedad real, devuelve null en vez de adivinar.

5. RENGLONES DE PARTIDA (line_items). Cuando se te pida extraer una lista de
   renglones repetidos (por ejemplo, partidas de una factura: cantidad,
   precio, descripción), extrae TODOS los renglones que encuentres dentro de
   la zona indicada, en el mismo orden en que aparecen en el documento. No
   asumas un número fijo de renglones. Si una línea no tiene claramente
   todos los valores requeridos en el orden esperado, OMÍTELA en vez de
   forzar una interpretación o inventar un valor faltante.

6. FORMATO DE SALIDA. Responde únicamente con un objeto JSON que cumpla
   exactamente el schema proporcionado. No incluyas explicaciones,
   comentarios, markdown, ni texto fuera del JSON.
"""


_ANCHOR_POSITION_TEXT = {
    TemplateField.AnchorPosition.AFTER: "inmediatamente después de ese texto, en la misma línea",
    TemplateField.AnchorPosition.BEFORE: "inmediatamente antes de ese texto",
    TemplateField.AnchorPosition.BELOW: "en la línea siguiente a ese texto",
}


def _describe_header_field(field: TemplateField, index: int) -> str:
    """Instrucción para un TemplateField con scope='header'."""
    position_desc = _ANCHOR_POSITION_TEXT.get(field.anchor_position, "cerca de ese texto")
    data_type = field.expected_data_type or "text"
    return (
        f'{index}. Campo "{field.layout_field.name}" (tipo esperado: {data_type})\n'
        f'   Ancla: busca el texto literal "{field.anchor_text}" en el documento.\n'
        f"   Posición: el valor está {position_desc}."
    )


def _describe_line_item_block(template, line_item_fields: list[TemplateField]) -> str:
    """
    Instrucción única para todo el bloque de renglones, ya que los campos
    line_item de un mismo template comparten la misma zona del documento.
    Se ordenan por layout_field.sort_order (posición esperada en la línea).
    """
    if not line_item_fields:
        return ""

    ordered = sorted(line_item_fields, key=lambda f: f.layout_field.sort_order)
    first = ordered[0]

    start_anchor = first.block_start_anchor
    end_anchor = first.block_end_anchor 

    campos_desc = ", ".join(
        f'"{f.layout_field.name}" ({f.expected_data_type or "text"})' for f in ordered
    )

    lines = ["RENGLONES DE PARTIDA A EXTRAER (lista, uno o más por documento):"]

    if start_anchor:
        lines.append(
            f'- Los renglones comienzan después del texto "{start_anchor}".'
        )
    else:
        lines.append(
            "- No hay un texto fijo que marque el inicio de los renglones; "
            "identifica la zona por el patrón de línea descrito abajo, "
            "antes del texto de cierre."
        )

    lines.append(f'- Los renglones terminan antes del texto "{end_anchor}".')
    lines.append(f"- Campos por renglón, en este orden: {campos_desc}.")

    if template.line_pattern_hint:
        lines.append(f"- Patrón de línea: {template.line_pattern_hint}")

    lines.append(
        "- Si el documento ya incluye una tabla estructurada (ver bloque "
        "TABLAS DETECTADAS más abajo) que corresponde a esta zona, "
        "prioriza esa tabla sobre el texto plano para separar los valores."
    )

    return "\n".join(lines)


def build_user_prompt(
    template,
    extracted_text: str,
    extracted_tables: list | None = None,
) -> str:
    """
    Arma el user prompt dinámico para un Template dado.

    Args:
        template: instancia de Template (document_type='pdf').
        extracted_text: texto plano extraído por pdfplumber.
        extracted_tables: lista de tablas detectadas por pdfplumber
            (pdfplumber_page.extract_tables()), o None/[] si no se detectó
            ninguna o el modo es text_only.
    """
    fields = list(
        template.fields.filter(extraction_type=TemplateField.ExtractionType.LLM_TEXT)
    )
    header_fields = [f for f in fields if f.scope == TemplateField.Scope.HEADER]
    line_item_fields = [f for f in fields if f.scope == TemplateField.Scope.LINE_ITEM]

    parts = [
        "DOCUMENTO A PROCESAR (texto extraído del PDF):",
        "---",
        extracted_text,
        "---",
    ]

    if extracted_tables:
        parts.append("\nTABLAS DETECTADAS (estructura fila/columna, si aplica):")
        for i, table in enumerate(extracted_tables, start=1):
            parts.append(f"Tabla {i}:")
            parts.append(str(table))

    if template.supplier_id and getattr(template, "hints", ""):
        # si decides mantener 'hints' en Template en vez de solo en
        # PdfExtractionConfig (ya eliminado), agrégalo aquí. Si no existe
        # el campo, esta sección simplemente no se incluye.
        parts.append(f"\nINSTRUCCIONES ESPECÍFICAS DE ESTE PROVEEDOR:\n{template.hints}")

    if header_fields:
        parts.append("\nCAMPOS DE ENCABEZADO A EXTRAER (un valor único por documento):")
        for i, field in enumerate(header_fields, start=1):
            parts.append(_describe_header_field(field, i))

    if line_item_fields:
        parts.append("\n" + _describe_line_item_block(template, line_item_fields))

    return "\n".join(parts)


def build_json_schema(template) -> dict:
    """
    JSON Schema forzado como structured output. Separa header (objeto plano)
    de line_items (array de objetos), ambos con valores string/null —
    nunca tipos especializados, la conversión real la hace NormalizationRule.
    """
    fields = list(
        template.fields.filter(extraction_type=TemplateField.ExtractionType.LLM_TEXT)
    )
    header_fields = [f for f in fields if f.scope == TemplateField.Scope.HEADER]
    line_item_fields = sorted(
        (f for f in fields if f.scope == TemplateField.Scope.LINE_ITEM),
        key=lambda f: f.layout_field.sort_order,
    )

    schema = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    if header_fields:
        header_properties = {
            f.layout_field.name: {
                "type": ["string", "null"],
                "description": f"Valor extraído para {f.layout_field.name}, "
                                f"tal como aparece en el texto fuente.",
            }
            for f in header_fields
        }
        schema["properties"]["header"] = {
            "type": "object",
            "properties": header_properties,
            "required": [f.layout_field.name for f in header_fields],
            "additionalProperties": False,
        }
        schema["required"].append("header")

    if line_item_fields:
        line_item_properties = {
            f.layout_field.name: {
                "type": ["string", "null"],
                "description": f"Valor extraído para {f.layout_field.name} "
                                f"en este renglón.",
            }
            for f in line_item_fields
        }
        schema["properties"]["line_items"] = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": line_item_properties,
                "required": [f.layout_field.name for f in line_item_fields],
                "additionalProperties": False,
            },
        }
        schema["required"].append("line_items")

    return schema