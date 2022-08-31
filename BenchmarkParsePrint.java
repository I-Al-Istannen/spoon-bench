import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import spoon.Launcher;

public class BenchmarkParsePrint {

  public static void main(String[] args) {
    if (args.length != 1) {
      System.err.println("Usage: BenchmarkParsePrint <folder to benchmark>");
      System.exit(1);
    }
    Launcher launcher = new Launcher();
    launcher.addInputResource(args[0]);
    launcher.getEnvironment().setComplianceLevel(17);

    Instant modelStart = Instant.now();
    launcher.buildModel();
    Duration modelDuration = Duration.between(modelStart, Instant.now());

    List<Duration> printDurations = new ArrayList<>();
    for (int i = 0; i < 1; i++) {
      Instant printStart = Instant.now();
      for (var cu : launcher.getFactory().CompilationUnit().getMap().values()) {
        cu.prettyprint();
      }
      printDurations.add(Duration.between(printStart, Instant.now()));
    }

    String output = "{"
        + "\"build_model\":"
        + "[" + modelDuration.toMillis() + "],"
        + "\"print_durations\":"
        + printDurations.stream().map(Duration::toMillis).collect(Collectors.toList())
        + "}";

    System.out.println(output);
  }
}
