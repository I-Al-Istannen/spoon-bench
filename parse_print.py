import json
from pathlib import Path
from subprocess import STDOUT, check_output

from common import (Benchmark, Interpretation, Measurement, SuccessMeasurement,
                    clone_guava, java_exe, print_header, print_info, print_success)


def measure_iteration(spoon_jar: Path, index_path: Path) -> dict[str, list[str]]:
    output = check_output(
        args=[
            java_exe(),
            "-cp",
            str(spoon_jar.absolute()),
            "BenchmarkParsePrint.java",
            str(index_path)
        ],
        stderr=STDOUT
    ).decode()
    print_success("  Iteration done")

    return json.loads([x for x in output.splitlines() if x.startswith('{"')][0])


def measure_parse_print(spoon_jar: Path) -> Benchmark:
    print_header("Parsing and printing Guava")
    guava_path = clone_guava() / "guava/src"

    print_info("Measuring data")
    measurements_data: dict[str, list[float]] = dict()
    for _ in range(0, 5):
        for name, durations in measure_iteration(spoon_jar, guava_path).items():
            if name in measurements_data:
                measurements_data[name] += [float(x) for x in durations]
            else:
                measurements_data[name] = [float(x) for x in durations]

    measurements: dict[str, Measurement] = dict()
    for name, values in measurements_data.items():
        measurements[name] = SuccessMeasurement(
            unit="ms",
            interpretation=Interpretation.LESS_IS_BETTER,
            values=values
        )

    return Benchmark(name="Guava", measurements=measurements)
