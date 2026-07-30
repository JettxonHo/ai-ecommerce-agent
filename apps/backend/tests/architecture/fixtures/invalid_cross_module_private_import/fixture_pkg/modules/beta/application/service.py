"""VIOLATION: beta reaches into alpha's private domain instead of alpha.public."""

from fixture_pkg.modules.alpha.domain.model import ALPHA_CONSTANT

COPIED = ALPHA_CONSTANT
