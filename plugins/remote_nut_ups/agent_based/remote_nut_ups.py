#!/usr/bin/env python3

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Service,
    Result,
    State,
    Metric,
)


# -----------------------------
# PARSER (multi-instance)
# -----------------------------
def parse_nut(string_table):
    data = {}
    for row in string_table:
        if len(row) != 3:
            continue  # ignore headers, empty lines, malformed rows
        ups_name, key, value = row
        data.setdefault(ups_name, {})[key] = value
    return data


agent_section_nut = AgentSection(
    name="remote_nut_ups",
    parse_function=parse_nut,
)


# -----------------------------
# DISCOVERY (one service per UPS)
# -----------------------------
def discover_nut(section):
    for ups_name in section:
        yield Service(item=ups_name)


# -----------------------------
# CHECK FUNCTION (per UPS)
# -----------------------------
def check_nut(item, params, section):
    ups = section.get(item)
    if not ups:
        return

    # Extract metrics from agent data
    bat = float(ups.get("battery.charge", 0))
    load = float(ups.get("ups.load", 0))
    temp = float(ups.get("ups.temperature", 0))
    volt_in = float(ups.get("input.voltage", 0))
    batt_volt = float(ups.get("battery.voltage", 0))
    volt_out = float(ups.get("output.voltage", 0))
    input_freq = float(ups.get("input.frequency", 0))
    status = ups.get("ups.status", "UNKNOWN")

    # Extract WATO parameters (dicts -> floats)
    bat_warn = float(params["battery_levels"]["warning"])
    bat_crit = float(params["battery_levels"]["critical"])

    bvolt_warn = float(params["battery_voltage_levels"]["warning"])
    bvolt_crit = float(params["battery_voltage_levels"]["critical"])

    involt_warn = float(params["input_voltage_levels"]["warning"])
    involt_crit = float(params["input_voltage_levels"]["critical"])

    outvolt_warn = float(params["output_voltage_levels"]["warning"])
    outvolt_crit = float(params["output_voltage_levels"]["critical"])

    freq_warn = float(params["frequency_levels"]["warning"])
    freq_crit = float(params["frequency_levels"]["critical"])

    # State logic
    state = State.OK

    if bat < bat_crit:
        state = State.CRIT
    elif bat < bat_warn:
        state = State.WARN

    if batt_volt < bvolt_crit:
        state = max(state, State.CRIT)
    elif batt_volt < bvolt_warn:
        state = max(state, State.WARN)

    if volt_in < involt_crit:
        state = max(state, State.CRIT)
    elif volt_in < involt_warn:
        state = max(state, State.WARN)

    if volt_out < outvolt_crit:
        state = max(state, State.CRIT)
    elif volt_out < outvolt_warn:
        state = max(state, State.WARN)

    # Frequency: symmetric window around nominal 50 Hz
    if input_freq < freq_crit or input_freq > (50 + (50 - freq_crit)):
        state = max(state, State.CRIT)
    elif input_freq < freq_warn or input_freq > (50 + (50 - freq_warn)):
        state = max(state, State.WARN)

    if status != "OL":
        state = max(state, State.WARN)

    # Summary
    yield Result(
        state=state,
        summary=(
            f"{item}: Battery {bat}% | Load {load}% | Temp {temp}°C | "
            f"Input {volt_in}V | Output {volt_out}V | "
            f"BattVolt {batt_volt}V | Freq {input_freq}Hz | Status {status}"
        ),
    )

    # Metrics
    yield Metric("battery_charge", bat, levels=(bat_warn, bat_crit))
    yield Metric("battery_voltage", batt_volt, levels=(bvolt_warn, bvolt_crit))
    yield Metric("ups_load", load)
    yield Metric("input_voltage", volt_in, levels=(involt_warn, involt_crit))
    yield Metric("ups_temperature", temp)
    yield Metric("output_voltage", volt_out, levels=(outvolt_warn, outvolt_crit))
    yield Metric("input_frequency", input_freq, levels=(freq_warn, freq_crit))


# -----------------------------
# CHECK PLUGIN DEFINITION
# -----------------------------
check_plugin_nut = CheckPlugin(
    name="remote_nut_ups",
    service_name="UPS NUT %s",
    discovery_function=discover_nut,
    check_function=check_nut,
    check_default_parameters={
        "battery_levels": {"warning": 20.0, "critical": 10.0},
        "battery_voltage_levels": {"warning": 11.0, "critical": 10.5},
        "input_voltage_levels": {"warning": 200.0, "critical": 180.0},
        "output_voltage_levels": {"warning": 200.0, "critical": 180.0},
        "frequency_levels": {"warning": 45.0, "critical": 40.0},
    },
    check_ruleset_name="remote_nut_ups",
)
