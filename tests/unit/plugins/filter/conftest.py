"""Shared fixtures for filter plugin tests."""

from __future__ import absolute_import, annotations, division, print_function

import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "plugins", "filter"),
)

from gnome_clocks import (  # noqa: E402 # pylint: disable=wrong-import-position,import-error
    FilterModule,
)


@pytest.fixture()
def filter_func():
    """Return the to_gnome_clocks filter function."""
    return FilterModule().filters()["to_gnome_clocks"]
