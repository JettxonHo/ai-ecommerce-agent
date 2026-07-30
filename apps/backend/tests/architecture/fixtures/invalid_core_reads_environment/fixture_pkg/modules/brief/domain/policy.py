"""VIOLATION: domain reads the process environment directly."""

import os

MODE = os.environ["BRIEF_MODE"]
