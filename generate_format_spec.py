import os
import re

def get_rs_files(dirs):
    for d in dirs:
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".rs"):
                    yield os.path.join(root, file)

def parse_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    types = []

    in_struct = False
    in_enum = False
    current_type = None
    brace_count = 0

    current_doc = []
    current_attrs = []

    for line in lines:
        stripped = line.strip()

        if not in_struct and not in_enum:
            if stripped.startswith("///"):
                current_doc.append(stripped[3:].strip())
            elif stripped.startswith("#["):
                current_attrs.append(stripped)
            elif stripped.startswith("pub struct ") or stripped.startswith("pub enum "):
                # also consider struct definitions like pub(crate) struct?
                # Actually most serializable types in format are pub struct/enum.
                is_serialize = any("Serialize" in a or "Deserialize" in a for a in current_attrs)

                kind = "struct" if stripped.startswith("pub struct ") else "enum"
                name_match = re.search(r'pub (struct|enum) (\w+)', stripped)
                name = name_match.group(2) if name_match else "Unknown"

                # if it's serializable, or if it's a version wrapper
                if is_serialize or name.startswith("RnoteFileMaj"):
                    current_type = {
                        "name": name,
                        "kind": kind,
                        "doc": "\n".join(current_doc),
                        "attrs": current_attrs.copy(),
                        "lines": [],
                        "filepath": filepath
                    }
                    if "{" in line:
                        if kind == "struct":
                            in_struct = True
                        else:
                            in_enum = True
                        brace_count = line.count("{") - line.count("}")
                        if brace_count == 0:
                            types.append(current_type)
                            current_type = None
                            in_struct = False
                            in_enum = False
                current_doc = []
                current_attrs = []
            elif not stripped.startswith("//") and stripped != "":
                current_doc = []
                if not stripped.startswith("#[") and not stripped.startswith("]"):
                    current_attrs = []

        else:
            if current_type:
                current_type["lines"].append(line)

            brace_count += line.count("{")
            brace_count -= line.count("}")

            if brace_count <= 0:
                if current_type:
                    # remove the last line if it's just a closing brace
                    if current_type["lines"] and current_type["lines"][-1].strip() == "}":
                        current_type["lines"] = current_type["lines"][:-1]
                    types.append(current_type)
                    current_type = None
                in_struct = False
                in_enum = False

    return types

def parse_fields_and_variants(t):
    elements = []

    current_doc = []
    current_attrs = []

    lines = t["lines"]

    # We parse the body to extract fields (for structs) or variants (for enums)
    # This is a bit tricky, we will just read line by line.

    brace_count = 0
    paren_count = 0
    bracket_count = 0

    for line in lines:
        stripped = line.strip()

        brace_count += line.count("{")
        brace_count -= line.count("}")
        paren_count += line.count("(")
        paren_count -= line.count(")")
        bracket_count += line.count("[")
        bracket_count -= line.count("]")

        if brace_count == 0 and paren_count == 0 and bracket_count == 0:
            if stripped.startswith("///"):
                current_doc.append(stripped[3:].strip())
            elif stripped.startswith("#["):
                current_attrs.append(stripped)
            elif stripped != "":
                # Could be a field or variant
                # e.g., `pub name: Type,` or `Variant,` or `Variant(Type),`

                # strip trailing comma
                if stripped.endswith(","):
                    stripped = stripped[:-1]

                name = ""
                rust_type = ""
                rename = ""

                for attr in current_attrs:
                    rename_match = re.search(r'rename\s*=\s*"([^"]+)"', attr)
                    if rename_match:
                        rename = rename_match.group(1)

                if t["kind"] == "struct":
                    # struct field
                    parts = stripped.split(":", 1)
                    if len(parts) == 2:
                        name = parts[0].replace("pub ", "").replace("pub(crate) ", "").strip()
                        rust_type = parts[1].strip()
                        elements.append({
                            "name": name,
                            "rename": rename if rename else name,
                            "type": rust_type,
                            "doc": "\n".join(current_doc)
                        })
                elif t["kind"] == "enum":
                    # enum variant
                    # either `Variant` or `Variant(Type)` or `Variant { field: Type }` (we don't handle { field: Type } well if it spans multiple lines, but enums in format are usually simpler)
                    if "(" in stripped:
                        name = stripped[:stripped.find("(")].strip()
                        rust_type = stripped[stripped.find("("):]
                    elif "{" in stripped:
                        name = stripped[:stripped.find("{")].strip()
                        rust_type = stripped[stripped.find("{"):]
                    else:
                        name = stripped
                        rust_type = ""

                    elements.append({
                        "name": name,
                        "rename": rename if rename else name,
                        "type": rust_type,
                        "doc": "\n".join(current_doc)
                    })

                current_doc = []
                current_attrs = []

    return elements

def main():
    files = list(get_rs_files(['crates/rnote-engine/src', 'crates/rnote-compose/src']))
    all_types = []
    for f in files:
        all_types.extend(parse_file(f))

    print(f"Found {len(all_types)} serializable types.")

    # filter and sort types to start from RnoteFileMaj0Min15 and then dependencies

    type_map = {t["name"]: t for t in all_types}

    # manually find the root and then trace dependencies
    # The root is RnoteFileMaj0Min15
    root = "RnoteFileMaj0Min15"

    visited = set()
    ordered = []

    def visit(name):
        if name in visited:
            return
        visited.add(name)
        if name in type_map:
            t = type_map[name]
            elements = parse_fields_and_variants(t)
            t["elements"] = elements
            ordered.append(t)

            # extract dependencies from types
            for el in elements:
                t_str = el["type"]
                # naive extraction of words that start with uppercase
                deps = re.findall(r'\b[A-Z][a-zA-Z0-9_]*\b', t_str)
                for d in deps:
                    if d in type_map:
                        visit(d)

    visit(root)
    visit("Document") # engine_snapshot might be an IValue, but we know it contains Document, Camera, etc.
    visit("EngineSnapshot")
    visit("Camera")
    visit("Stroke")
    visit("ChronoComponent")

    # also add RnotefileWrapper manually from crates/rnote-engine/src/fileformats/rnoteformat/mod.rs

    with open('docs/rnote_file_format_spec.md', 'w', encoding='utf-8') as f:
        f.write("# Rnote File Format Specification\n\n")
        f.write("The `.rnote` file format is a gzipped JSON file. At the root, it contains a wrapper with a version and the data.\n\n")

        f.write("## Root Structure\n\n")
        f.write("```json\n{\n  \"version\": \"0.15.0\",\n  \"data\": { ... }\n}\n```\n\n")

        f.write("The `data` field contains the serialized `RnoteFileMaj0Min15` object, which encapsulates the `engine_snapshot`.\n\n")

        for t in ordered:
            f.write(f"## `{t['name']}` ({t['kind']})\n\n")
            if t["doc"]:
                f.write(f"{t['doc']}\n\n")

            if t["kind"] == "struct":
                f.write("| Field | Type | Description |\n")
                f.write("|---|---|---|\n")
                for el in t["elements"]:
                    f.write(f"| `{el['rename']}` | `{el['type']}` | {el['doc'].replace(chr(10), ' ')} |\n")
            elif t["kind"] == "enum":
                f.write("| Variant | Type | Description |\n")
                f.write("|---|---|---|\n")
                for el in t["elements"]:
                    f.write(f"| `{el['rename']}` | `{el['type']}` | {el['doc'].replace(chr(10), ' ')} |\n")
            f.write("\n")

main()
