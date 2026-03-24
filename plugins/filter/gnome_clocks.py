"""Filter plugin to generate GVariant strings for GNOME world clocks."""

# Author: Brant Evans
# License: GPL-3.0-or-later

from __future__ import absolute_import, annotations, division, print_function

import math

from typing import TYPE_CHECKING

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native

if TYPE_CHECKING:
    from typing import Any, Callable


__metaclass__ = type  # pylint: disable=C0103

DOCUMENTATION = """
    name: to_gnome_clocks
    author: Brant Evans
    version_added: "1.1.0"
    short_description: Convert a list of locations to a GNOME world-clocks GVariant string.
    description:
      - Accepts a list of location dictionaries and produces the GVariant string
        expected by GNOME dconf world-clock keys.
      - By default the output uses the C(dict) wrapping required by
        C(/org/gnome/clocks/world-clocks).
      - Pass C(shell=true) to produce the C(variant) wrapping required by
        C(/org/gnome/shell/world-clocks/locations).
    positional: _input
    options:
      _input:
        description:
          - A list of location dictionaries.
          - Each dictionary must contain C(city) and C(code).
          - Optional keys are C(is_city) (default C(false)), C(coords) and
            C(parent_coords) (each a two-element C([latitude, longitude]) list
            of floats in radians).
        type: list
        elements: dict
        required: true
      shell:
        description:
          - "When C(false) (default), wrap each location as
            C({'location': <TUPLE>}) for C(/org/gnome/clocks/world-clocks)."
          - "When C(true), wrap each location as C(<TUPLE>) for
            C(/org/gnome/shell/world-clocks/locations)."
        type: bool
        default: false
"""

EXAMPLES = """
# Define locations once, use the filter for both dconf keys.

- name: Set GNOME world clocks
  vars:
    world_clock_locations:
      - city: Chicago
        code: KMDW
        is_city: true
        coords: [0.72927128935316143, -1.5316185371029443]
        parent_coords: [0.73042086791828009, -1.529781996944241]
      - city: Raleigh
        code: KRDU
        coords: [0.62605930672100707, -1.3750818938070426]
        parent_coords: [0.62605930672100707, -1.3750818938070426]
      - city: "Coordinated Universal Time (UTC)"
        code: "@UTC"
  ansible.builtin.debug:
    msg:
      clocks: "{{ world_clock_locations | branic.system_management.to_gnome_clocks }}"
      shell: "{{ world_clock_locations | branic.system_management.to_gnome_clocks(shell=true) }}"
"""


def _serialize_location(loc: dict[str, Any]) -> str:
    """Build the inner GVariant tuple for a single world-clock location.

    Returns a string like::

        (uint32 2, <('Chicago', 'KMDW', true, [(0.729..., -1.531...)], [(0.730..., -1.529...)])>)
    """
    city = loc["city"]
    code = loc["code"]
    is_city = "true" if loc.get("is_city", False) else "false"

    coords = loc.get("coords")
    parent_coords = loc.get("parent_coords")

    if coords:
        coords_str = f"[({coords[0]:.17g}, {coords[1]:.17g})]"
    else:
        coords_str = "@a(dd) []"

    if parent_coords:
        parent_str = f"[({parent_coords[0]:.17g}, {parent_coords[1]:.17g})]"
    else:
        parent_str = "@a(dd) []"

    return f"(uint32 2, <('{city}', '{code}', {is_city}, {coords_str}, {parent_str})>)"


def _to_gnome_clocks(locations: Any, shell: bool = False) -> str:
    """Convert a list of location dicts to a GNOME world-clocks GVariant string.

    Args:
        locations: List of location dictionaries.
        shell: When True, produce the variant-wrapped format for
               /org/gnome/shell/world-clocks/locations.

    Returns:
        The GVariant string suitable for dconf.
    """
    if not isinstance(locations, list):
        raise AnsibleFilterError(
            f"to_gnome_clocks expects a list, got {type(locations).__name__}",
        )

    items = []
    for i, loc in enumerate(locations):
        if not isinstance(loc, dict):
            raise AnsibleFilterError(
                f"to_gnome_clocks: item {i} is not a dict",
            )
        try:
            for key in ("city", "code"):
                if key not in loc:
                    raise AnsibleFilterError(
                        f"to_gnome_clocks: item {i} is missing required key '{key}'",
                    )

            for key in ("coords", "parent_coords"):
                val = loc.get(key)
                if val is not None:
                    if not isinstance(val, list) or len(val) != 2:
                        raise AnsibleFilterError(
                            f"to_gnome_clocks: item {i} key '{key}' must be a two-element list",
                        )
                    for idx, elem in enumerate(val):
                        if not isinstance(elem, (int, float)):
                            raise AnsibleFilterError(
                                f"to_gnome_clocks: item {i} key '{key}[{idx}]'"
                                f" must be a number, got {type(elem).__name__}",
                            )
                    lat, lon = val
                    if not -math.pi / 2 <= lat <= math.pi / 2:
                        raise AnsibleFilterError(
                            f"to_gnome_clocks: item {i} key '{key}[0]' (latitude)"
                            f" {lat} is outside valid radian range"
                            f" [{-math.pi / 2:.4f}, {math.pi / 2:.4f}]",
                        )
                    if not -math.pi <= lon <= math.pi:
                        raise AnsibleFilterError(
                            f"to_gnome_clocks: item {i} key '{key}[1]' (longitude)"
                            f" {lon} is outside valid radian range"
                            f" [{-math.pi:.4f}, {math.pi:.4f}]",
                        )

            serialized = _serialize_location(loc)
        except AnsibleFilterError:
            raise
        except Exception as e:
            raise AnsibleFilterError(
                f"to_gnome_clocks: failed to serialize item {i}: {to_native(e)}",
            ) from e

        if shell:
            items.append(f"<{serialized}>")
        else:
            items.append(f"{{'location': <{serialized}>}}")

    return f"[{', '.join(items)}]"


class FilterModule:
    """Ansible filter plugin for GNOME world-clock GVariant generation."""

    def filters(self) -> dict[str, Callable]:
        """Map filter names to their functions.

        Returns:
            dict: The filter plugin functions.
        """
        return {"to_gnome_clocks": _to_gnome_clocks}
