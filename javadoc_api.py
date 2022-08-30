
import json
import shutil
from pathlib import Path
from subprocess import STDOUT, check_output

from common import (Benchmark, Interpretation, Measurement, SuccessMeasurement, clone_guava,
                    print_header, print_info, print_success)


def clone_javadoc_api() -> Path:
    print_info("Cloning JavadocApi")
    directory = Path("/tmp/JavadocApi")
    if directory.exists():
        print_success("Existed already")
        return directory
        # shutil.rmtree(directory)

    check_output(
        [
            "git",
            "clone",
            "https://github.com/I-Al-Istannen/JavadocApi",
            str(directory)
        ],
        stderr=STDOUT
    )
    print_success("  Cloning finished")

    return directory


def write_javadoc_api_config(javadoc_api_path: Path, path_to_index: Path) -> Path:
    text = """
    {
      "outputPath": "",
      "resourcePaths": [
        "{{PATH}}"
      ],
      "allowedPackages": [
        "*"
      ],
      "outputTimings": true
    }
    """.replace("{{PATH}}", str(path_to_index.absolute()))

    path = javadoc_api_path / "javadocapi-config.json"
    with open(path, "w") as file:
        file.write(text)

    return path


def patch_javadoc_api(javadoc_api_path: Path, spoon_jar: Path):
    print_info("Patching javadoc api...")

    if (javadoc_api_path / "target/JavadocApi.jar").exists():
        print_success("Skipped patch (build was present)")
        return


    with open("JavadocApi.patch.template", "r") as file:
        text = file.read().replace("{{PATH}}", str(spoon_jar))

    with open(javadoc_api_path / "JavadocApi.patch", "w") as file:
        file.write(text)

    check_output(
        args=["patch < JavadocApi.patch"],
        shell=True,
        cwd=javadoc_api_path,
        stderr=STDOUT
    )
    print_success("  Patched")


def build_javadoc_api(javadoc_api_path: Path):
    print_info("Building JavadocApi")

    if (javadoc_api_path / "target/JavadocApi.jar").exists():
        print_success("Skipped build (was present)")
        return

    check_output(
        args=["mvn", "clean", "package"],
        cwd=javadoc_api_path,
        env={"JAVA_HOME": "/home/bench/.sdkman/candidates/java/current"},
        stderr=STDOUT
    )
    print_success("  Built")


def run_javadoc_api_iteration(spoon_jar: Path, javadoc_api_path: Path, config_path: Path) -> dict[str, float]:
    javadocapi_jar = javadoc_api_path / "target/JavadocApi.jar"

    output = check_output(
        args=[
            "/home/bench/.sdkman/candidates/java/current/bin/java",
            "-cp",
            f"{str(spoon_jar.absolute())}:" +
            str(javadocapi_jar.absolute()),
            "de.ialistannen.javadocapi.indexing.Indexer",
            str(config_path.absolute())
        ],
        cwd=javadoc_api_path,
        stderr=STDOUT
    ).decode()
    print_success("  Run finished")

    return json.loads([x for x in output.splitlines() if x.startswith('{"')][0])


def run_javadoc_api(spoon_jar: Path, javadoc_api_path: Path, config_path: Path) -> Benchmark:
    print_info("Running JavadocApi")

    data: dict[str, list[float]] = dict()
    for _ in range(5):
        for name, val in run_javadoc_api_iteration(spoon_jar, javadoc_api_path, config_path).items():
            if name in data:
                data[name].append(val)
            else:
                data[name] = [val]

    measurements: dict[str, Measurement] = dict()
    for name, duration in data.items():
        measurements[name] = SuccessMeasurement(
            unit="ms",
            interpretation=Interpretation.LESS_IS_BETTER,
            values=duration
        )

    return Benchmark(name="JavadocApi", measurements=measurements)


def measure_javadoc_api(spoon_jar: Path):
    print_header("Running JavadocApi")
    javadoc_api = clone_javadoc_api()
    guava_path = clone_guava() / "guava/src"

    patch_javadoc_api(javadoc_api, spoon_jar)
    build_javadoc_api(javadoc_api)

    config = write_javadoc_api_config(javadoc_api, guava_path)

    return run_javadoc_api(spoon_jar, javadoc_api, config)
