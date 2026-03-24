"""Unit tests for branic.system_management.plugins.filter.gnome_clocks."""

from __future__ import absolute_import, annotations, division, print_function

import math

import pytest

from ansible.errors import AnsibleFilterError

CHICAGO = {
    "city": "Chicago",
    "code": "KMDW",
    "is_city": True,
    "coords": [0.72927128935316143, -1.5316185371029443],
    "parent_coords": [0.73042086791828009, -1.529781996944241],
}

RALEIGH = {
    "city": "Raleigh",
    "code": "KRDU",
    "coords": [0.62605930672100707, -1.3750818938070426],
    "parent_coords": [0.62605930672100707, -1.3750818938070426],
}

UTC = {
    "city": "Coordinated Universal Time (UTC)",
    "code": "@UTC",
}


class TestSingleLocationAllFields:
    """A single location with every field populated."""

    def test_default_wrapping(self, filter_func):
        """Default output wraps each location in a dict with 'location' key."""
        result = filter_func([CHICAGO])
        assert result.startswith("[{'location': <")
        assert result.endswith(">}]")
        assert "'Chicago'" in result
        assert "'KMDW'" in result
        assert "true" in result
        assert "uint32 2" in result

    def test_shell_wrapping(self, filter_func):
        """shell=True wraps each location as a bare variant."""
        result = filter_func([CHICAGO], shell=True)
        assert result.startswith("[<")
        assert result.endswith(">]")
        assert "{'location'" not in result


class TestMultipleLocations:
    """The real-world case: Chicago + Raleigh + UTC."""

    def test_default_three_locations(self, filter_func):
        """All three locations appear in the default output."""
        result = filter_func([CHICAGO, RALEIGH, UTC])
        assert result.count("{'location': <") == 3
        assert "'Chicago'" in result
        assert "'Raleigh'" in result
        assert "'Coordinated Universal Time (UTC)'" in result

    def test_shell_three_locations(self, filter_func):
        """shell=True produces three comma-separated variants."""
        result = filter_func([CHICAGO, RALEIGH, UTC], shell=True)
        assert "{'location'" not in result
        assert result.startswith("[<")
        assert result.count(">, <") == 2


class TestNoCoordinates:
    """A location with only city and code produces empty typed arrays."""

    def test_empty_arrays(self, filter_func):
        """UTC entry uses @a(dd) [] for both coordinate arrays."""
        result = filter_func([UTC])
        assert "@a(dd) []" in result
        assert "'@UTC'" in result

    def test_utc_is_not_city(self, filter_func):
        """UTC defaults to is_city=false."""
        result = filter_func([UTC])
        assert "false, @a(dd)" in result


class TestIsCityDefault:
    """is_city defaults to false when omitted."""

    def test_raleigh_defaults_false(self, filter_func):
        """Raleigh (no is_city key) serializes as false."""
        result = filter_func([RALEIGH])
        assert "'KRDU', false," in result

    def test_chicago_explicit_true(self, filter_func):
        """Chicago (is_city=True) serializes as true."""
        result = filter_func([CHICAGO])
        assert "'KMDW', true," in result


class TestCoordinateSerialization:
    """Coordinates are serialized with full precision."""

    def test_coords_in_output(self, filter_func):
        """Station coordinates preserve 17 significant digits."""
        result = filter_func([CHICAGO])
        assert "0.72927128935316143" in result
        assert "-1.5316185371029443" in result

    def test_parent_coords_in_output(self, filter_func):
        """Parent coordinates preserve 17 significant digits."""
        result = filter_func([CHICAGO])
        assert "0.73042086791828009" in result
        assert "-1.529781996944241" in result


class TestEmptyList:
    """An empty list produces an empty GVariant array."""

    def test_default_empty(self, filter_func):
        """Empty input returns '[]'."""
        assert filter_func([]) == "[]"

    def test_shell_empty(self, filter_func):
        """Empty input with shell=True also returns '[]'."""
        assert filter_func([], shell=True) == "[]"


class TestErrorMissingCity:
    """Missing 'city' key raises AnsibleFilterError."""

    def test_missing_city(self, filter_func):
        """A dict without 'city' is rejected."""
        with pytest.raises(AnsibleFilterError, match="missing required key 'city'"):
            filter_func([{"code": "KMDW"}])


class TestErrorMissingCode:
    """Missing 'code' key raises AnsibleFilterError."""

    def test_missing_code(self, filter_func):
        """A dict without 'code' is rejected."""
        with pytest.raises(AnsibleFilterError, match="missing required key 'code'"):
            filter_func([{"city": "Chicago"}])


class TestErrorBadCoords:
    """coords with wrong length raises AnsibleFilterError."""

    def test_coords_one_element(self, filter_func):
        """A single-element coords list is rejected."""
        with pytest.raises(AnsibleFilterError, match="must be a two-element list"):
            filter_func([{"city": "X", "code": "Y", "coords": [1.0]}])

    def test_coords_three_elements(self, filter_func):
        """A three-element coords list is rejected."""
        with pytest.raises(AnsibleFilterError, match="must be a two-element list"):
            filter_func([{"city": "X", "code": "Y", "coords": [1.0, 2.0, 3.0]}])

    def test_parent_coords_bad(self, filter_func):
        """A single-element parent_coords list is rejected."""
        with pytest.raises(AnsibleFilterError, match="must be a two-element list"):
            filter_func([{"city": "X", "code": "Y", "parent_coords": [1.0]}])

    def test_coords_non_numeric(self, filter_func):
        """String coordinate values are rejected."""
        with pytest.raises(AnsibleFilterError, match="must be a number, got str"):
            filter_func([{"city": "X", "code": "Y", "coords": ["foo", "bar"]}])

    def test_coords_mixed_types(self, filter_func):
        """A mix of float and string coordinate values is rejected."""
        with pytest.raises(AnsibleFilterError, match="must be a number"):
            filter_func([{"city": "X", "code": "Y", "coords": [0.5, "bar"]}])

    def test_coords_int_accepted(self, filter_func):
        """Integer coordinate values are accepted."""
        result = filter_func([{"city": "X", "code": "Y", "coords": [0, 0]}])
        assert "[(0," in result


class TestErrorCoordsOutOfRange:
    """Coordinates outside valid radian range raise AnsibleFilterError."""

    def test_latitude_too_high(self, filter_func):
        """Latitude above pi/2 is rejected."""
        with pytest.raises(AnsibleFilterError, match="latitude.*outside valid radian range"):
            filter_func([{"city": "X", "code": "Y", "coords": [2.0, 0.0]}])

    def test_latitude_too_low(self, filter_func):
        """Latitude below -pi/2 is rejected."""
        with pytest.raises(AnsibleFilterError, match="latitude.*outside valid radian range"):
            filter_func([{"city": "X", "code": "Y", "coords": [-2.0, 0.0]}])

    def test_longitude_too_high(self, filter_func):
        """Longitude above pi is rejected."""
        with pytest.raises(AnsibleFilterError, match="longitude.*outside valid radian range"):
            filter_func([{"city": "X", "code": "Y", "coords": [0.0, 4.0]}])

    def test_longitude_too_low(self, filter_func):
        """Longitude below -pi is rejected."""
        with pytest.raises(AnsibleFilterError, match="longitude.*outside valid radian range"):
            filter_func([{"city": "X", "code": "Y", "coords": [0.0, -4.0]}])

    def test_degrees_caught(self, filter_func):
        """Passing degrees (e.g. Chicago 41.88) is caught by the latitude check."""
        with pytest.raises(AnsibleFilterError, match="latitude.*outside valid radian range"):
            filter_func([{"city": "Chicago", "code": "KMDW", "coords": [41.88, -87.63]}])

    def test_parent_coords_validated(self, filter_func):
        """parent_coords are validated the same as coords."""
        with pytest.raises(AnsibleFilterError, match="parent_coords.*latitude"):
            filter_func([{"city": "X", "code": "Y", "parent_coords": [2.0, 0.0]}])

    def test_boundary_values_accepted(self, filter_func):
        """Values at exactly pi/2 and pi are valid."""
        result = filter_func(
            [{"city": "X", "code": "Y", "coords": [math.pi / 2, math.pi]}],
        )
        assert "uint32 2" in result


class TestErrorNonList:
    """Non-list input raises AnsibleFilterError."""

    def test_string_input(self, filter_func):
        """A string input is rejected."""
        with pytest.raises(AnsibleFilterError, match="expects a list"):
            filter_func("not a list")

    def test_dict_input(self, filter_func):
        """A dict input is rejected."""
        with pytest.raises(AnsibleFilterError, match="expects a list"):
            filter_func({"city": "X", "code": "Y"})

    def test_non_dict_item(self, filter_func):
        """A list containing a non-dict item is rejected."""
        with pytest.raises(AnsibleFilterError, match="not a dict"):
            filter_func(["not a dict"])
