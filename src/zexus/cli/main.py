# ~/zexus-interpreter/src/zexus/cli/main.py
import click
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table

# Import your existing modules
from ..lexer import Lexer
from ..parser import Parser
from ..evaluator import eval_node, Environment
from ..syntax_validator import SyntaxValidator  # NEW IMPORT

console = Console()

@click.group()
@click.version_option(version="0.1.0", prog_name="Zexus")
@click.option('--syntax-style', type=click.Choice(['universal', 'tolerable', 'auto']), 
              default='auto', help='Syntax style to use (universal=strict, tolerable=flexible)')
@click.pass_context
def cli(ctx, syntax_style):
    """Zexus Programming Language - Declarative, intent-based programming"""
    ctx.ensure_object(dict)
    ctx.obj['SYNTAX_STYLE'] = syntax_style

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def run(ctx, file):
    """Run a Zexus program"""
    try:
        with open(file, 'r') as f:
            source_code = f.read()

        console.print(f"🚀 [bold green]Running[/bold green] {file}\n")
        
        # NEW: Syntax validation before running
        syntax_style = ctx.obj['SYNTAX_STYLE']
        validator = SyntaxValidator()
        
        # Auto-detect syntax style if needed
        if syntax_style == 'auto':
            syntax_style = validator.suggest_syntax_style(source_code)
            console.print(f"🔍 [bold blue]Detected syntax style:[/bold blue] {syntax_style}")
        
        # Validate syntax
        validation_result = validator.validate_code(source_code, syntax_style)
        if not validation_result['is_valid']:
            console.print(f"[bold yellow]⚠️  Syntax warnings: {validation_result['error_count']} issue(s) found[/bold yellow]")
            for suggestion in validation_result['suggestions']:
                severity_emoji = "❌" if suggestion['severity'] == 'error' else "⚠️"
                console.print(f"  {severity_emoji} Line {suggestion['line']}: {suggestion['message']}")
            
            # Auto-fix if there are errors
            if any(s['severity'] == 'error' for s in validation_result['suggestions']):
                console.print("[bold yellow]🛠️  Attempting auto-fix...[/bold yellow]")
                fixed_code, fix_result = validator.auto_fix(source_code, syntax_style)
                if fix_result['applied_fixes'] > 0:
                    console.print(f"✅ [bold green]Applied {fix_result['applied_fixes']} fixes[/bold green]")
                    source_code = fixed_code
                else:
                    console.print("[bold red]❌ Could not auto-fix errors, attempting to run anyway...[/bold red]")

        # Run the program using your existing code
        lexer = Lexer(source_code)
        parser = Parser(lexer, syntax_style)  # NEW: Pass syntax_style to parser
        program = parser.parse_program()

        if parser.errors:
            console.print("[bold red]Parser Errors:[/bold red]")
            for error in parser.errors:
                console.print(f"  ❌ {error}")
            return

        env = Environment()
        result = eval_node(program, env)

        if result and hasattr(result, 'inspect') and result.inspect() != 'null':
            console.print(f"\n✅ [bold green]Result:[/bold green] {result.inspect()}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def check(ctx, file):
    """Check syntax of a Zexus file with detailed validation"""
    try:
        with open(file, 'r') as f:
            source_code = f.read()

        syntax_style = ctx.obj['SYNTAX_STYLE']
        validator = SyntaxValidator()
        
        # Auto-detect syntax style if needed
        if syntax_style == 'auto':
            syntax_style = validator.suggest_syntax_style(source_code)
            console.print(f"🔍 [bold blue]Detected syntax style:[/bold blue] {syntax_style}")
        
        # Run syntax validation
        validation_result = validator.validate_code(source_code, syntax_style)
        
        # Also run parser for additional validation
        lexer = Lexer(source_code)
        parser = Parser(lexer, syntax_style)
        program = parser.parse_program()

        # Display results
        if parser.errors or not validation_result['is_valid']:
            console.print("[bold red]❌ Syntax Issues Found:[/bold red]")
            
            # Show parser errors first
            for error in parser.errors:
                console.print(f"  🚫 Parser: {error}")
            
            # Show validator suggestions
            for suggestion in validation_result['suggestions']:
                severity_icon = "🚫" if suggestion['severity'] == 'error' else "⚠️"
                console.print(f"  {severity_icon} Validator: {suggestion['message']}")
                
            # Show warnings
            for warning in validation_result['warnings']:
                console.print(f"  ⚠️  Warning: {warning['message']}")
                
            sys.exit(1)
        else:
            console.print("[bold green]✅ Syntax is valid![/bold green]")
            if validation_result['warnings']:
                console.print("\n[bold yellow]ℹ️  Warnings:[/bold yellow]")
                for warning in validation_result['warnings']:
                    console.print(f"  ⚠️  {warning['message']}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def validate(ctx, file):
    """Validate and auto-fix Zexus syntax"""
    try:
        with open(file, 'r') as f:
            source_code = f.read()

        syntax_style = ctx.obj['SYNTAX_STYLE']
        validator = SyntaxValidator()
        
        # Auto-detect syntax style if needed
        if syntax_style == 'auto':
            syntax_style = validator.suggest_syntax_style(source_code)
            console.print(f"🔍 [bold blue]Detected syntax style:[/bold blue] {syntax_style}")
        
        console.print(f"📝 [bold blue]Validating with {syntax_style} syntax...[/bold blue]")
        
        # Run validation and auto-fix
        fixed_code, validation_result = validator.auto_fix(source_code, syntax_style)
        
        # Show results
        if validation_result['is_valid']:
            console.print("[bold green]✅ Code is valid![/bold green]")
        else:
            console.print(f"[bold yellow]🛠️  Applied {validation_result['applied_fixes']} fixes[/bold yellow]")
            console.print("[bold yellow]⚠️  Remaining issues:[/bold yellow]")
            
            for suggestion in validation_result['suggestions']:
                severity_icon = "🚫" if suggestion['severity'] == 'error' else "⚠️"
                console.print(f"  {severity_icon} Line {suggestion['line']}: {suggestion['message']}")
            
            for warning in validation_result['warnings']:
                console.print(f"  ⚠️  Warning: {warning['message']}")
        
        # Write fixed code back to file if changes were made
        if validation_result['applied_fixes'] > 0:
            with open(file, 'w') as f:
                f.write(fixed_code)
            console.print(f"💾 [bold green]Updated {file} with fixes[/bold green]")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def ast(ctx, file):
    """Show AST of a Zexus file"""
    try:
        with open(file, 'r') as f:
            source_code = f.read()

        syntax_style = ctx.obj['SYNTAX_STYLE']
        validator = SyntaxValidator()
        
        # Auto-detect syntax style if needed
        if syntax_style == 'auto':
            syntax_style = validator.suggest_syntax_style(source_code)
            console.print(f"🔍 [bold blue]Detected syntax style:[/bold blue] {syntax_style}")

        lexer = Lexer(source_code)
        parser = Parser(lexer, syntax_style)  # NEW: Pass syntax_style
        program = parser.parse_program()

        console.print(Panel.fit(
            str(program),
            title=f"[bold blue]Abstract Syntax Tree ({syntax_style} syntax)[/bold blue]",
            border_style="blue"
        ))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def tokens(ctx, file):
    """Show tokens of a Zexus file"""
    try:
        with open(file, 'r') as f:
            source_code = f.read()

        syntax_style = ctx.obj['SYNTAX_STYLE']
        validator = SyntaxValidator()
        
        # Auto-detect syntax style if needed
        if syntax_style == 'auto':
            syntax_style = validator.suggest_syntax_style(source_code)
            console.print(f"🔍 [bold blue]Detected syntax style:[/bold blue] {syntax_style}")

        lexer = Lexer(source_code)

        table = Table(title=f"Tokens ({syntax_style} syntax)")
        table.add_column("Type", style="cyan")
        table.add_column("Literal", style="green")
        table.add_column("Line", style="yellow")
        table.add_column("Column", style="yellow")

        while True:
            token = lexer.next_token()
            if token.type == "EOF":
                break
            table.add_row(token.type, token.literal, str(token.line), str(token.column))

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@cli.command()
@click.pass_context
def repl(ctx):
    """Start Zexus REPL"""
    syntax_style = ctx.obj['SYNTAX_STYLE']
    env = Environment()
    validator = SyntaxValidator()
    
    console.print("[bold green]Zexus REPL v0.1.0[/bold green]")
    console.print(f"📝 [bold blue]Syntax style: {syntax_style}[/bold blue]")
    console.print("Type 'exit' to quit\n")

    while True:
        try:
            code = console.input("[bold blue]>>> [/bold blue]")
            if code.strip() in ['exit', 'quit']:
                break

            if not code.strip():
                continue

            # Validate syntax in REPL
            if syntax_style != 'auto':
                validation_result = validator.validate_code(code, syntax_style)
                if not validation_result['is_valid']:
                    for suggestion in validation_result['suggestions']:
                        if suggestion['severity'] == 'error':
                            console.print(f"[red]Syntax: {suggestion['message']}[/red]")
                    # Continue anyway for REPL flexibility

            lexer = Lexer(code)
            parser = Parser(lexer, syntax_style)  # NEW: Pass syntax_style
            program = parser.parse_program()

            if parser.errors:
                for error in parser.errors:
                    console.print(f"[red]Parser: {error}[/red]")
                continue

            result = eval_node(program, env)
            if result and hasattr(result, 'inspect') and result.inspect() != 'null':
                console.print(f"[green]{result.inspect()}[/green]")

        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!")
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

@cli.command()
@click.pass_context
def init(ctx):
    """Initialize a new Zexus project"""
    syntax_style = ctx.obj['SYNTAX_STYLE']
    project_name = click.prompt("Project name", default="my-zexus-app")

    project_path = Path(project_name)
    project_path.mkdir(exist_ok=True)

    # Create basic structure
    (project_path / "src").mkdir()
    (project_path / "tests").mkdir()

    # Choose template based on syntax style
    if syntax_style == "universal":
        main_content = '''# Welcome to Zexus! (Universal Syntax)

let app_name = "My Zexus App"

action main() {
    print("🚀 Hello from " + app_name)
    print("✨ Running Zexus v0.1.0")
    
    # Test some features
    let numbers = [1, 2, 3, 4, 5]
    let doubled = numbers.map(transform: it * 2)
    print("Doubled numbers: " + string(doubled))
}

main()
'''
    else:
        # Tolerable or auto - use flexible syntax
        main_content = '''# Welcome to Zexus! (Flexible Syntax)

let app_name = "My Zexus App"

action main():
    print "🚀 Hello from " + app_name
    print "✨ Running Zexus v0.1.0"
    
    # Test some features
    let numbers = [1, 2, 3, 4, 5]
    let doubled = numbers.map(transform: it * 2)
    print "Doubled numbers: " + string(doubled)

main()
'''

    (project_path / "main.zx").write_text(main_content)

    # Create utils file
    if syntax_style == "universal":
        utils_content = '''# Utility functions (Universal Syntax)

action add(a: integer, b: integer) -> integer {
    return a + b
}

action multiply(a: integer, b: integer) -> integer {
    return a * b
}

action greet(name: text) -> text {
    return "Hello, " + name + "!"
}
'''
    else:
        utils_content = '''# Utility functions (Flexible Syntax)

action add(a: integer, b: integer) -> integer:
    return a + b

action multiply(a: integer, b: integer) -> integer:
    return a * b

action greet(name: text) -> text:
    return "Hello, " + name + "!"
'''

    (project_path / "src" / "utils.zx").write_text(utils_content)

    # Create config file
    config_content = '''{
    "name": "''' + project_name + '''",
    "version": "0.1.0",
    "type": "application",
    "entry_point": "main.zx",
    "syntax_style": "''' + syntax_style + '''"
}
'''

    (project_path / "zexus.json").write_text(config_content)

    console.print(f"\n✅ [bold green]Project '{project_name}' created![/bold green]")
    console.print(f"📁 cd {project_name}")
    console.print("🚀 zx run main.zx")
    console.print(f"📝 [bold blue]Using {syntax_style} syntax style[/bold blue]")

if __name__ == "__main__":
    cli()