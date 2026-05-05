import sys
import os

# Add root to path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.isp_info import get_isp_info
from core.ping_test import run_ping_test
from core.stability import run_stability_test
from core.speed_test import run_speed_test

from cli.reporter import (
    print_header,
    print_isp_panel,
    print_ping_panel,
    print_speed_panel,
    print_stability_panel,
    print_summary,
    print_footer,
)

console = Console()


def run_all_tests(stability_duration=30):
    """
    Run all network tests in sequence and display results.
    stability_duration : how long to run stability test in seconds
    """

    print_header()

    # ── Step 1 — ISP Info ─────────────────────────────────────────
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Fetching ISP information...[/cyan]"),
        transient=True,
    ) as progress:
        progress.add_task("isp")
        isp_result = get_isp_info()

    print_isp_panel(isp_result)

    # ── Step 2 — Ping Test ────────────────────────────────────────
    with Progress(
        SpinnerColumn(),
        TextColumn("[magenta]Running ping test...[/magenta]"),
        transient=True,
    ) as progress:
        progress.add_task("ping")
        ping_result = run_ping_test(count=10)

    print_ping_panel(ping_result)

    # ── Step 3 — Speed Test ───────────────────────────────────────
    console.print("\n[yellow]Running speed test — this may take 30-60 seconds...[/yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[yellow]Testing download and upload speeds...[/yellow]"),
        transient=True,
    ) as progress:
        progress.add_task("speed")
        speed_result = run_speed_test()

    print_speed_panel(speed_result)

    # ── Step 4 — Stability Test ───────────────────────────────────
    console.print(f"\n[blue]Running stability test for {stability_duration} seconds...[/blue]")

    stability_result = run_stability_test(duration=stability_duration)

    print_stability_panel(stability_result)

    # ── Step 5 — Summary ──────────────────────────────────────────
    print_summary(isp_result, ping_result, speed_result, stability_result)

    print_footer()


def main():
    """Entry point with argument handling"""
    import argparse

    parser = argparse.ArgumentParser(
        description="wire-test — Network Speed & Stability Analyzer"
    )
    parser.add_argument(
        "--stability-duration",
        type=int,
        default=30,
        help="Duration of stability test in seconds (default: 30)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run a quick test with 10 second stability test"
    )

    args = parser.parse_args()

    if args.quick:
        stability_duration = 10
    else:
        stability_duration = args.stability_duration

    try:
        run_all_tests(stability_duration=stability_duration)
    except KeyboardInterrupt:
        console.print("\n\n[red]Test interrupted by user.[/red]")
        sys.exit(0)


if __name__ == "__main__":
    main()