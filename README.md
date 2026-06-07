# cmk_nut_ups

# Remote NUT UPS Monitoring for Checkmk 2.5 (API2)

This package provides full monitoring of remote NUT (Network UPS Tools) devices via Checkmk 2.5 (tested with this version) using the modern **Agent-Based API v2** and **Rulesets API v2**. So it may actually be comaptible with version 2.3+.

It supports:

- Monitoring **multiple UPS devices per host**
- One Checkmk service **per UPS**
- Thresholds configurable via **WATO ruleset**
- Perfdata for graphing (battery, voltages, frequency, load, temperature)
- Clean API2-compliant implementation (no legacy WATO code)

---

## Components

### 1. Agent Plugin  
`local/share/check_mk/agents/plugins/remote_nut_ups`

This script:

- Reads a list of NUT hosts from `nut_hosts.cfg`
- Discovers all UPS devices via `upsc -l`
- Queries each UPS individually
- Emits namespaced metrics in the form:

<<<nut>>>
ups1 battery.charge 100
ups1 input.voltage 230
ups2 battery.charge 95
ups2 input.voltage 228


This enables **multi-instance parsing** on the Checkmk side.

---

### 2. Check Plugin  
`local/lib/python3/cmk_addons/plugins/remote_nut_ups/agent_based/remote_nut_ups.py`

Implements:

- Multi-instance parsing (`{ups_name: {key: value}}`)
- One service per UPS (`UPS NUT %s`)
- Threshold evaluation using parameters from the ruleset
- Perfdata output for all metrics

Metrics include:

- `battery_charge`
- `battery_voltage`
- `input_voltage`
- `output_voltage`
- `input_frequency`
- `ups_load`
- `ups_temperature`

---

### 3. Ruleset  
`local/lib/python3/cmk_addons/plugins/remote_nut_ups/rulesets/remote_nut_ups_parameters.py`

Defines configurable thresholds for:

- Battery charge
- Battery voltage
- Input voltage
- Output voltage
- Input frequency

The ruleset uses Checkmk **Rulesets API v2** (`cmk.rulesets.v1`) and provides
tuple-style `(warn, crit)` parameters matching the check plugin.

---

## Installation

Install by using the provided MKP package.

## Usage

After installation, Checkmk will automatically discover:

UPS NUT ups1
UPS NUT ups2
UPS NUT ups3

Code

Each UPS gets its own:

- State evaluation
- Thresholds
- Metrics
- Graphs
- Notifications

Thresholds can be configured globally or per-host via WATO under:

Setup → Service Monitoring Rules → Remote NUT UPS parameters
