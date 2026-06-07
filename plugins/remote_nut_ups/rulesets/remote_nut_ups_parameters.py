#!/usr/bin/env python3

from cmk.rulesets.v1 import Help, Title, Label
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    Topic,
)


def _pair(title: str, warn: float, crit: float) -> DictElement:
    """
    A reusable helper that returns a Dictionary with two Float fields.
    This version ensures Checkmk returns actual floats, not strings.
    """
    return DictElement(
        parameter_form=Dictionary(
            title=Title(title),
            elements={
                "warning": DictElement(
                    parameter_form=Float(
                        title=Label("Warning below"),
                        prefill=DefaultValue(warn),
                    ),
                    required=True,
                ),
                "critical": DictElement(
                    parameter_form=Float(
                        title=Label("Critical below"),
                        prefill=DefaultValue(crit),
                    ),
                    required=True,
                ),
            },
        ),
        required=True,
    )


def _parameter_valuespec_remote_nut_ups() -> Dictionary:
    """
    The full parameter dictionary for all UPS thresholds.
    All values are guaranteed to be floats when passed to the check plugin.
    """
    return Dictionary(
        title=Title("Remote NUT UPS parameters"),
        help_text=Help("Thresholds for battery, voltage and frequency."),
        elements={
            "battery_levels": _pair(
                "Battery charge levels",
                20.0,
                10.0,
            ),
            "battery_voltage_levels": _pair(
                "Battery voltage levels",
                11.0,
                10.5,
            ),
            "input_voltage_levels": _pair(
                "Input voltage levels",
                200.0,
                180.0,
            ),
            "output_voltage_levels": _pair(
                "Output voltage levels",
                200.0,
                180.0,
            ),
            "frequency_levels": _pair(
                "Input frequency levels",
                45.0,
                40.0,
            ),
        },
    )


rule_spec_remote_nut_ups = CheckParameters(
    name="remote_nut_ups",
    title=Title("Remote NUT UPS parameters"),
    topic=Topic.ENVIRONMENTAL,
    condition=HostAndItemCondition(
        item_title=Title("UPS"),
    ),
    parameter_form=_parameter_valuespec_remote_nut_ups,
)
