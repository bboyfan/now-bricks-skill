#!/usr/bin/env python3
"""
validate_bricks_json.py
Comprehensive validator for Bricks Builder 2.4+ JSON structures.
Supports Clipboard format, Template Export format, and direct Postmeta elements arrays.
"""

import sys
import json
import re

def validate_bricks_data(data, filepath="<stream>"):
    errors = []
    warnings = []

    # 1. Determine format
    if isinstance(data, list):
        elements = data
        global_classes = []
        fmt = "Direct Elements Array (Postmeta / API)"
    elif isinstance(data, dict):
        if "source" in data and data.get("source") == "bricksCopiedElements":
            fmt = "Clipboard Format (bricksCopiedElements)"
        elif "templateType" in data or "templateSettings" in data or "global_classes" in data:
            fmt = "Template Export Format (Bricks Template Import)"
        else:
            fmt = "Generic Bricks Document Object"
        
        elements = data.get("content", data.get("header", data.get("footer", [])))
        global_classes = data.get("global_classes", data.get("globalClasses", []))
    else:
        return False, ["Root JSON must be either a list of elements or a dictionary with 'content' array."], []

    if not isinstance(elements, list) or len(elements) == 0:
        return False, ["Elements array ('content') is missing or empty."], []

    print(f"[{filepath}] Detected format: {fmt}")
    print(f"[{filepath}] Total elements: {len(elements)}")

    ids = set()
    element_map = {}

    # 2. Check IDs & Types
    for idx, el in enumerate(elements):
        if not isinstance(el, dict):
            errors.append(f"Element at index {idx} is not an object/dict: {el}")
            continue

        eid = el.get("id")
        ename = el.get("name")

        if not eid:
            errors.append(f"Element at index {idx} ({ename}) is missing 'id'.")
            continue

        if len(eid) != 6:
            warnings.append(f"Element ID '{eid}' is not standard 6 alphanumeric characters.")

        if eid in ids:
            errors.append(f"Duplicate element ID detected: '{eid}'")
        ids.add(eid)
        element_map[eid] = el

        if not ename:
            errors.append(f"Element '{eid}' is missing 'name' (element type).")

        # 3. Check Settings type
        settings = el.get("settings")
        if settings is None:
            pass # Bricks allows missing settings
        elif isinstance(settings, list):
            errors.append(f"Element '{eid}' has settings as a list []. Bricks requires a dictionary {{}}.")
        elif isinstance(settings, dict):
            # Check custom CSS
            css_custom = settings.get("_cssCustom")
            if isinstance(css_custom, str) and "%root%" in css_custom:
                warnings.append(f"Element '{eid}' contains '%root%' in _cssCustom. In Bricks 2.4+ programmatic JSON, write '#brxe-{eid}' (or '.brxe-{eid}' in components) for direct CSS rendering.")
        else:
            errors.append(f"Element '{eid}' has invalid settings type: {type(settings)}")

        # 4. Check Component Instances
        if "cid" in el:
            if el.get("children") and len(el.get("children")) > 0:
                warnings.append(f"Element '{eid}' has 'cid' (component instance) but also defines 'children'. In Bricks, component instances should not overwrite children.")

    # 5. Check Tree Hierarchy & Parent/Children matching
    roots = []
    for eid, el in element_map.items():
        parent = el.get("parent")
        children = el.get("children", [])

        if parent in (0, "0"):
            roots.append(el)
            if el.get("name") not in ("section", "header", "footer", "div", "container"):
                warnings.append(f"Root element '{eid}' is type '{el.get('name')}'. Sections are recommended at root.")
        else:
            if parent not in ids:
                errors.append(f"Element '{eid}' specifies non-existent parent '{parent}'.")
            else:
                parent_el = element_map[parent]
                parent_children = parent_el.get("children", [])
                if eid not in parent_children:
                    errors.append(f"Hierarchy mismatch: Element '{eid}' has parent '{parent}', but parent's children does not include '{eid}'.")

        for child_id in children:
            if child_id not in ids:
                errors.append(f"Element '{eid}' lists non-existent child '{child_id}'.")
            else:
                child_el = element_map[child_id]
                if child_el.get("parent") != eid:
                    errors.append(f"Hierarchy mismatch: Element '{eid}' lists child '{child_id}', but child's parent is '{child_el.get('parent')}'.")

    if len(roots) == 0:
        errors.append("No root elements found (all elements have non-zero parents, forming a cycle or disconnected tree).")

    # 6. Check Global Classes references
    have_classes = {c["id"] for c in global_classes if isinstance(c, dict) and "id" in c}
    for eid, el in element_map.items():
        settings = el.get("settings", {})
        if isinstance(settings, dict):
            used_classes = settings.get("_cssGlobalClasses", [])
            if isinstance(used_classes, list):
                for cls_id in used_classes:
                    if global_classes and cls_id not in have_classes:
                        warnings.append(f"Element '{eid}' references class ID '{cls_id}', which is not bundled in global_classes.")

    success = len(errors) == 0
    return success, errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_bricks_json.py <file.json> [file2.json ...]")
        sys.exit(1)

    all_passed = True
    for filepath in sys.argv[1:]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[{filepath}] JSON Parse Error: {e}")
            all_passed = False
            continue

        passed, errors, warnings = validate_bricks_data(data, filepath)
        
        if warnings:
            print(f"[{filepath}] Warnings ({len(warnings)}):")
            for w in warnings[:10]:
                print(f"  [WARN] {w}")
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more warnings.")

        if not passed:
            print(f"[{filepath}] Validation FAILED with {len(errors)} errors:")
            for err in errors[:15]:
                print(f"  [ERR] {err}")
            if len(errors) > 15:
                print(f"  ... and {len(errors) - 15} more errors.")
            all_passed = False
        else:
            print(f"[{filepath}] Validation PASSED (100% compliant with Bricks Builder structure)!\n")

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
