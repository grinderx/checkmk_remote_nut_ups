# Remote NUT UPS monitoring for Checkmk 2.3+ (API2)

This package provides full monitoring of remote NUT (Network UPS Tools) devices via Checkmk 2.5 (tested with this version) using the modern **Agent-Based API v2** and **Rulesets API v2**. So it may actually be compatible with version 2.3+.

It supports:

- Monitoring **multiple UPS devices per host**
- One Checkmk service **per UPS**
- Thresholds configurable via **WATO ruleset**
- Perfdata for graphing (battery, voltages, frequency, load, temperature)
- Clean API2-compliant implementation

This project is licensed under the GNU General Public License v2.0 or, at your option, any later version.

See the LICENSE file for details.

Note: AI assisted.

---

## Components

### 1. Agent Plugin  
`/opt/omd/sites/site_name/local/share/check_mk/agents/plugins/remote_nut_ups`

This script:

- Reads a list of remote NUT hosts from `/opt/omd/sites/site_name/local/share/check_mk/agents/plugins/remote_nut_ups_hosts.cfg`
- Discovers all UPS devices via `upsc -l`
- Queries each UPS individually
- Emits namespaced metrics in the form:

```text
<<<<remote_ups_host_01>>>>
<<<remote_ups_nut>>>
ups1 battery.charge 100
ups1 input.voltage 230
ups2 battery.charge 95
ups2 input.voltage 228
<<<<remote_ups_host_02>>>>
<<<remote_ups_nut>>>
ups1 battery.charge 100
ups1 input.voltage 230
ups2 battery.charge 95
ups2 input.voltage 228
```

This enables **multi-instance parsing** on the Checkmk side.

---

### 2. Check Plugin  
`/opt/omd/sites/site_name/local/lib/python3/cmk_addons/plugins/remote_nut_ups/agent_based/remote_nut_ups.py`

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
`/opt/omd/sites/site_name/local/lib/python3/cmk_addons/plugins/remote_nut_ups/rulesets/remote_nut_ups_parameters.py`

Defines configurable thresholds for:

- Battery charge
- Battery voltage
- Input voltage
- Output voltage
- Input frequency

---

## Installation

Install by using the provided MKP package which you can find here:

## Usage

After installation, Checkmk will automatically discover:

```text
UPS NUT ups1
UPS NUT ups2
UPS NUT ups3
```

per remote NUT host. Each UPS gets its own:

- State evaluation
- Thresholds
- Metrics
- Graphs
- Notifications

Thresholds can be configured globally or per-host via WATO under:

Setup → Service Monitoring Rules → Remote NUT UPS parameters
