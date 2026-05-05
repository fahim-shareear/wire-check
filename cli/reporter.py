from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def get_quality_color(label):
    """Map quality labels to colors"""
    colors = {
        "Excellent": "bright_green",
        "Good":      "green",
        "Average":   "yellow",
        "Fair":      "yellow",
        "Poor":      "red",
        "Unknown":   "grey50",
    }
    return colors.get(label, "white")


def colored_label(label):
    """Return a colored rich Text object for a quality label"""
    color = get_quality_color(label)
    return f"[{color}]{label}[/{color}]"


def print_header():
    """Print the app header"""
    console.print()
    console.print(Rule("[bold cyan]⚡ WIRE-TEST — Network Speed Analyzer[/bold cyan]"))
    console.print()


def print_isp_panel(isp_result):
    """Display ISP information in a panel"""
    if not isp_result["success"]:
        console.print(f"[red]ISP Info Error: {isp_result['error']}[/red]")
        return

    data = isp_result["data"]

    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    table.add_column("Key",   style="bold cyan",  width=16)
    table.add_column("Value", style="white")

    table.add_row("IP Address",  data["ip"])
    table.add_row("ISP / Org",   data["isp"])
    table.add_row("City",        data["city"])
    table.add_row("Region",      data["region"])
    table.add_row("Country",     data["country"])
    table.add_row("Timezone",    data["timezone"])
    table.add_row("Timestamp",   data["timestamp"])

    console.print(Panel(table, title="[bold cyan]🌐 Network Identity[/bold cyan]", border_style="cyan"))


def print_ping_panel(ping_result):
    """Display ping and latency results in a panel"""
    if not ping_result["success"]:
        console.print(f"[red]Ping Error: {ping_result['error']}[/red]")
        return

    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    table.add_column("Key",   style="bold magenta", width=20)
    table.add_column("Value", style="white")

    table.add_row("Host",             ping_result["host"])
    table.add_row("Packets Sent",     str(ping_result["packets_sent"]))
    table.add_row("Packets Received", str(ping_result["packets_received"]))
    table.add_row("Packet Loss",      f"{ping_result['packet_loss']}%")
    table.add_row("Min Latency",      f"{ping_result['min_latency']} ms")
    table.add_row("Avg Latency",      f"{ping_result['avg_latency']} ms")
    table.add_row("Max Latency",      f"{ping_result['max_latency']} ms")
    table.add_row("Jitter",           f"{ping_result['jitter']} ms")
    table.add_row("Ping Quality",     colored_label(ping_result["ping_quality"]))
    table.add_row("Jitter Quality",   colored_label(ping_result["jitter_quality"]))
    table.add_row("Loss Quality",     colored_label(ping_result["loss_quality"]))

    console.print(Panel(table, title="[bold magenta]🏓 Ping & Latency[/bold magenta]", border_style="magenta"))


def print_speed_panel(speed_result):
    """Display speed test results in a panel"""
    if not speed_result["success"]:
        console.print(f"[red]Speed Test Error: {speed_result['error']}[/red]")
        return

    server = speed_result["server"]

    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    table.add_column("Key",   style="bold yellow", width=20)
    table.add_column("Value", style="white")

    table.add_row("Server",           f"{server['name']}, {server['country']}")
    table.add_row("Sponsor",          server["sponsor"])
    table.add_row("Server Latency",   f"{server['latency']} ms")
    table.add_row("Download Speed",   f"[bold]{speed_result['download_mbps']} Mbps[/bold]")
    table.add_row("Upload Speed",     f"[bold]{speed_result['upload_mbps']} Mbps[/bold]")
    table.add_row("Download Quality", colored_label(speed_result["download_quality"]))
    table.add_row("Upload Quality",   colored_label(speed_result["upload_quality"]))

    console.print(Panel(table, title="[bold yellow]🚀 Speed Test[/bold yellow]", border_style="yellow"))


def print_stability_panel(stability_result):
    """Display stability test results in a panel"""
    if not stability_result["success"]:
        console.print(f"[red]Stability Error: {stability_result['error']}[/red]")
        return

    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    table.add_column("Key",   style="bold blue", width=20)
    table.add_column("Value", style="white")

    score_color = get_quality_color(stability_result["stability_label"])

    table.add_row("Duration",         f"{stability_result['duration']}s")
    table.add_row("Total Pings",      str(stability_result["total_pings"]))
    table.add_row("Successful",       str(stability_result["successful_pings"]))
    table.add_row("Failed",           str(stability_result["failed_pings"]))
    table.add_row("Packet Loss",      f"{stability_result['packet_loss']}%")
    table.add_row("Avg Latency",      f"{stability_result['avg_latency']} ms")
    table.add_row("Jitter",           f"{stability_result['jitter']} ms")
    table.add_row("Latency Range",    f"{stability_result['latency_range']} ms")
    table.add_row("Connection Type",  stability_result["connection_type"])
    table.add_row("Stability Score",  f"[{score_color}][bold]{stability_result['stability_score']}/100[/bold][/{score_color}]")
    table.add_row("Stability Label",  colored_label(stability_result["stability_label"]))

    console.print(Panel(table, title="[bold blue]📊 Connection Stability[/bold blue]", border_style="blue"))


def print_summary(isp_result, ping_result, speed_result, stability_result):
    """Print a final summary panel with key metrics"""
    lines = []

    if isp_result["success"]:
        lines.append(f"[cyan]ISP[/cyan]        : {isp_result['data']['isp']}")

    if ping_result["success"]:
        lines.append(f"[magenta]Ping[/magenta]       : {ping_result['avg_latency']} ms — {colored_label(ping_result['ping_quality'])}")

    if speed_result["success"]:
        lines.append(f"[yellow]Download[/yellow]   : {speed_result['download_mbps']} Mbps — {colored_label(speed_result['download_quality'])}")
        lines.append(f"[yellow]Upload[/yellow]     : {speed_result['upload_mbps']} Mbps — {colored_label(speed_result['upload_quality'])}")

    if stability_result["success"]:
        lines.append(f"[blue]Stability[/blue]  : {stability_result['stability_score']}/100 — {colored_label(stability_result['stability_label'])}")

    summary_text = "\n".join(lines)
    console.print(Panel(summary_text, title="[bold white]📋 Summary[/bold white]", border_style="white"))


def print_footer():
    """Print the app footer"""
    console.print()
    console.print(Rule("[grey50]wire-test — Network Diagnostics Complete[/grey50]"))
    console.print()