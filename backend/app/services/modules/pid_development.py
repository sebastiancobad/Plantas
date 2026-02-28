"""
P&ID Development Engine (Module 11).

Implements:
    - ISA 5.1 instrument symbol definitions and tag generation
    - Automated line numbering per PIP PIC001
    - Equipment tag numbering convention
    - P&ID drawing data model (JSON-exportable for frontend rendering)

Standards: ISA 5.1 (2009), PIP PIC001, PIP PIID001
"""

import uuid


# ── ISA 5.1 Instrument Letter Codes ────────────────────────────────
ISA_FIRST_LETTER = {
    "A": "Analysis", "B": "Burner/Combustion", "C": "Conductivity",
    "D": "Density", "E": "Voltage", "F": "Flow",
    "G": "Gaging/Position", "H": "Hand (manual)", "I": "Current",
    "J": "Power", "K": "Time/Schedule", "L": "Level",
    "M": "Moisture", "N": "User Choice", "O": "User Choice",
    "P": "Pressure", "Q": "Quantity", "R": "Radiation",
    "S": "Speed/Frequency", "T": "Temperature", "U": "Multivariable",
    "V": "Vibration", "W": "Weight/Force", "X": "Unclassified",
    "Y": "Event/State", "Z": "Position/Dimension",
}

ISA_SUCCEEDING_LETTERS = {
    "A": "Alarm", "C": "Controller", "E": "Element/Sensor",
    "G": "Glass/Gauge", "H": "High", "I": "Indicator",
    "K": "Control Station", "L": "Low", "R": "Recorder",
    "S": "Switch", "T": "Transmitter", "V": "Valve",
    "Y": "Relay/Compute", "Z": "Final Element",
}

# ── ISA Symbol Types ────────────────────────────────────────────────
ISA_SYMBOLS = {
    "field_instrument": {
        "shape": "circle",
        "description": "Field-mounted instrument",
        "example": "FT-101 (Flow Transmitter)",
    },
    "control_room_instrument": {
        "shape": "circle_with_line",
        "description": "Control room instrument (shared display)",
        "example": "FIC-101 (Flow Indicating Controller)",
    },
    "dcs_function": {
        "shape": "square",
        "description": "DCS/PLC function block",
        "example": "TIC-201 in DCS",
    },
    "sis_function": {
        "shape": "diamond",
        "description": "Safety Instrumented System function",
        "example": "PSHH-101 (Pressure Switch High-High, SIS)",
    },
    "control_valve": {
        "shape": "butterfly_body",
        "description": "Control valve with actuator",
        "example": "FCV-101",
    },
    "on_off_valve": {
        "shape": "butterfly_body_discrete",
        "description": "On/off (block) valve",
        "example": "XV-101",
    },
    "check_valve": {
        "shape": "check",
        "description": "Check (non-return) valve",
        "example": "In pipe line",
    },
    "relief_valve": {
        "shape": "relief",
        "description": "Pressure relief valve",
        "example": "PSV-101",
    },
}


def _generate_line_number(unit_number: str, sequence: int,
                           diameter_inches: float, spec_class: str,
                           fluid_code: str, insulation: str = "") -> str:
    """
    Generate a line number per PIP PIC001 convention.

    Format: [diameter]-[fluid]-[sequence]-[spec]-[insulation]
    Example: 6"-HC-101-A1A-HT

    Args:
        unit_number: Unit/area code (e.g., "10")
        sequence: Sequential line number
        diameter_inches: Nominal pipe size
        spec_class: Piping spec class (e.g., "A1A", "B2B")
        fluid_code: Fluid service code (e.g., "HC", "CW", "ST")
        insulation: Insulation code (e.g., "HT", "CS", "PP")
    """
    dia = f"{diameter_inches:.0f}\""
    line_num = f"{dia}-{fluid_code}-{unit_number}{sequence:03d}-{spec_class}"
    if insulation:
        line_num += f"-{insulation}"
    return line_num


def _generate_instrument_tag(first_letter: str, succeeding: str,
                               loop_number: int, suffix: str = "") -> str:
    """Generate ISA 5.1 compliant instrument tag."""
    tag = f"{first_letter}{succeeding}-{loop_number:03d}"
    if suffix:
        tag += suffix
    return tag


def generate_pid_data(input_data: dict) -> dict:
    """
    Generate P&ID drawing data model for a process node.

    Returns a JSON structure that the frontend can render using React Flow.
    """
    calc_id = f"pid-{uuid.uuid4().hex[:8]}"

    unit_number = input_data.get("unit_number", "10")
    equipment = input_data.get("equipment", [])
    instruments = input_data.get("instruments", [])
    lines = input_data.get("lines", [])

    # ── Equipment Nodes ─────────────────────────────────────────────
    eq_nodes = []
    for i, eq in enumerate(equipment):
        eq_nodes.append({
            "id": eq.get("tag", f"EQ-{unit_number}{i+1:02d}"),
            "type": eq.get("type", "vessel"),
            "label": eq.get("tag", f"EQ-{unit_number}{i+1:02d}"),
            "description": eq.get("description", ""),
            "position": {"x": eq.get("x", 100 + i * 200), "y": eq.get("y", 200)},
        })

    # ── Instrument Nodes ────────────────────────────────────────────
    inst_nodes = []
    for inst in instruments:
        first = inst.get("measured_variable", "T")[0].upper()
        succeeding = inst.get("function", "IC")
        loop = inst.get("loop_number", 101)
        tag = _generate_instrument_tag(first, succeeding, loop, inst.get("suffix", ""))

        symbol_type = "dcs_function"
        if inst.get("location") == "field":
            symbol_type = "field_instrument"
        elif inst.get("location") == "control_room":
            symbol_type = "control_room_instrument"
        if inst.get("sis", False):
            symbol_type = "sis_function"

        inst_nodes.append({
            "id": tag,
            "type": "instrument",
            "symbol": ISA_SYMBOLS.get(symbol_type, ISA_SYMBOLS["field_instrument"]),
            "tag": tag,
            "measured_variable": ISA_FIRST_LETTER.get(first, "Unknown"),
            "function": succeeding,
            "position": {"x": inst.get("x", 150), "y": inst.get("y", 100)},
        })

    # ── Process Lines ───────────────────────────────────────────────
    line_objs = []
    for i, line in enumerate(lines):
        line_num = _generate_line_number(
            unit_number, i + 1,
            line.get("diameter_inches", 6),
            line.get("spec_class", "A1A"),
            line.get("fluid_code", "HC"),
            line.get("insulation", ""),
        )
        line_objs.append({
            "id": line_num,
            "from_equipment": line.get("from", ""),
            "to_equipment": line.get("to", ""),
            "line_number": line_num,
            "diameter_inches": line.get("diameter_inches", 6),
            "spec_class": line.get("spec_class", "A1A"),
            "fluid": line.get("fluid_code", "HC"),
            "insulated": bool(line.get("insulation", "")),
        })

    # ── Valve Nodes ─────────────────────────────────────────────────
    valve_nodes = []
    for v in input_data.get("valves", []):
        valve_nodes.append({
            "id": v.get("tag", "XV-101"),
            "type": v.get("type", "control_valve"),
            "tag": v.get("tag", "XV-101"),
            "symbol": ISA_SYMBOLS.get(v.get("type", "control_valve"),
                                       ISA_SYMBOLS["control_valve"]),
            "on_line": v.get("on_line", ""),
            "fail_position": v.get("fail_position", "FC"),
        })

    return {
        "status": "success",
        "calculation_id": calc_id,
        "drawing_data": {
            "equipment_nodes": eq_nodes,
            "instrument_nodes": inst_nodes,
            "valve_nodes": valve_nodes,
            "process_lines": line_objs,
        },
        "tag_summary": {
            "equipment_count": len(eq_nodes),
            "instrument_count": len(inst_nodes),
            "valve_count": len(valve_nodes),
            "line_count": len(line_objs),
        },
        "isa_reference": {
            "first_letters": ISA_FIRST_LETTER,
            "succeeding_letters": ISA_SUCCEEDING_LETTERS,
            "symbol_types": {k: v["description"] for k, v in ISA_SYMBOLS.items()},
        },
    }
