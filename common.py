
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import shutil
from subprocess import STDOUT, check_output
import sys
from typing import Any, Union


DIM = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
CYAN = "\033[36m"

BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(header: Any, end: str = "\n"):
    print("\n" + BOLD + CYAN + str(header) + RESET, end=end, file=sys.stderr)


def print_info(info: Any, end: str = "\n"):
    print(BLUE + str(info + RESET), end=end, file=sys.stderr)


def print_success(message: Any, end: str = "\n"):
    print(GREEN + str(message) + RESET, end=end, file=sys.stderr)


class Interpretation(str, Enum):
    LESS_IS_BETTER = "LESS_IS_BETTER"
    MORE_IS_BETTER = "MORE_IS_BETTER"
    NEUTRAL = "NEUTRAL"


@dataclass
class SuccessMeasurement:
    unit: str
    interpretation: Interpretation
    values: list[float]

    def to_dict(self):
        return self.__dict__


@dataclass
class ErrorMeasurement:
    unit: str
    interpretation: Interpretation
    error: str

    def to_dict(self):
        return self.__dict__


Measurement = Union[SuccessMeasurement, ErrorMeasurement]


@dataclass
class Benchmark:
    name: str
    measurements: dict[str, Measurement]

    def to_dict(self):
        vals = dict()
        for name, measurement in self.measurements.items():
            vals[name] = measurement.to_dict()

        return {self.name: vals}


def java_home():
    return "/home/bench/.sdkman/candidates/java/current/"


def java_exe():
    return java_home() + "/bin/java"


def clone_guava() -> Path:
    print_info("Cloning guava")
    guava_path = Path("/tmp/guava")

    if guava_path.exists():
        print_success("Existed already")
        return guava_path
        # shutil.rmtree(guava_path)

    check_output(
        args=["git", "clone", "https://github.com/google/guava", str(guava_path)],
        stderr=STDOUT
    )
    check_output(
        args=["git", "checkout", "807a5938700ba4041bf8fa4d1a1ebbc040b04906"],
        stderr=STDOUT,
        cwd=guava_path
    )

    print_success("  Cloned")

    return guava_path
