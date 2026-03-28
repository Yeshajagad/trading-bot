import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from bot.logging_config import setup_logging
from bot.client import BinanceClient, BinanceClientError
from bot.orders import OrderManager
from bot.validators import validate_order_inputs, ValidationError

setup_logging()
console = Console()
app = typer.Typer()

@app.command()
def place(
    symbol: str = typer.Option(..., help="Symbol e.g. BTCUSDT"),
    side: str = typer.Option(..., help="BUY or SELL"),
    order_type: str = typer.Option(..., "--type", help="MARKET, LIMIT, STOP_MARKET"),
    quantity: float = typer.Option(..., help="Quantity to trade"),
    price: Optional[float] = typer.Option(None, help="Limit price"),
    stop_price: Optional[float] = typer.Option(None, help="Stop price"),
):
    try:
        cleaned = validate_order_inputs(symbol=symbol, side=side, order_type=order_type, quantity=quantity, price=price, stop_price=stop_price)
    except ValidationError as e:
        console.print(f"\n[bold red]❌ Validation Error:[/bold red] {e}\n")
        raise typer.Exit(code=1)
    try:
        client = BinanceClient()
    except Exception as e:
        console.print(f"\n[bold red]❌ Client Error:[/bold red] {e}\n")
        raise typer.Exit(code=1)
    mode_str = "📄 PAPER TRADING" if client._mode == "paper" else "🔴 LIVE"
    console.print(Panel.fit(f"[bold cyan]⚡ Trading Bot[/bold cyan]\nMode: {mode_str}", border_style="cyan"))
    t = Table(title="📋 Order Request", box=box.ROUNDED, border_style="blue")
    t.add_column("Field", style="bold white")
    t.add_column("Value", style="cyan")
    t.add_row("Symbol", cleaned["symbol"])
    t.add_row("Side", f"[green]{cleaned['side']}[/green]" if cleaned["side"] == "BUY" else f"[red]{cleaned['side']}[/red]")
    t.add_row("Order Type", cleaned["order_type"])
    t.add_row("Quantity", str(cleaned["quantity"]))
    if cleaned.get("price"):
        t.add_row("Price", f"${cleaned['price']:,.2f}")
    if cleaned.get("stop_price"):
        t.add_row("Stop Price", f"${cleaned['stop_price']:,.2f}")
    console.print(t)
    confirmed = typer.confirm("\n🚀 Confirm and place this order?")
    if not confirmed:
        console.print("\n[yellow]Order cancelled.[/yellow]\n")
        raise typer.Exit()
    try:
        manager = OrderManager(client)
        response = manager.place_order(symbol=cleaned["symbol"], side=cleaned["side"], order_type=cleaned["order_type"], quantity=cleaned["quantity"], price=cleaned.get("price"), stop_price=cleaned.get("stop_price"))
    except BinanceClientError as e:
        console.print(f"\n[bold red]❌ Exchange Error:[/bold red] {e}\n")
        raise typer.Exit(code=1)
    r = Table(title="✅ Order Response", box=box.ROUNDED, border_style="green")
    r.add_column("Field", style="bold white")
    r.add_column("Value", style="bright_green")
    r.add_row("Order ID", str(response.get("orderId", "N/A")))
    r.add_row("Symbol", str(response.get("symbol", "N/A")))
    r.add_row("Status", str(response.get("status", "N/A")))
    r.add_row("Side", str(response.get("side", "N/A")))
    r.add_row("Type", str(response.get("type", "N/A")))
    r.add_row("Orig Qty", str(response.get("origQty", "N/A")))
    r.add_row("Executed Qty", str(response.get("executedQty", "N/A")))
    r.add_row("Avg Price", str(response.get("avgPrice", "0")))
    console.print(r)
    console.print("\n[bold green]🎉 Order placed successfully![/bold green]\n")

if __name__ == "__main__":
    app()
