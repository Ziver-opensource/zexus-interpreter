# zpm.py

import click
import json
import os
import subprocess

# --- SIMULATED ZEXUS PACKAGE REGISTRY ---
REGISTRY = {
    "zexus-spec": "https://github.com/Zaidux/zexus-language-design.git",
    "CoolUI": "https://github.com/Zaidux/zexus-language-design.git",
    "ton-utils": "https://github.com/Zaidux/zexus-language-design.git"
}
# -----------------------------------------

@click.group()
def cli():
    """Zexus Package Manager"""
    pass

@cli.command()
@click.option('--zdk', is_flag=True, help='Initialize a Zexus smart contract project.')
def init(zdk):
    """Initializes a new project."""
    if zdk:
        click.echo("Initializing Zexus Blockchain Development Kit project...")
        click.echo("(This feature is planned for a future version)")
        return

    click.echo("This utility will walk you through creating a zexus.json file.")
    click.echo("Press ^C at any time to quit.\n")
    project_name = click.prompt("Project Name", default=os.path.basename(os.getcwd()))
    version = click.prompt("Version", default="1.0.0")
    description = click.prompt("Description", default="")
    author = click.prompt("Author", default="")
    main_file = click.prompt("Main file", default="app.zx")
    zexus_config = { "name": project_name, "version": version, "description": description, "author": author, "main": main_file, "scripts": { "start": f"zx {main_file}", "test": "echo \"Error: no test specified\" && exit 1" }, "dependencies": {} }
    try:
        with open('zexus.json', 'w') as f: json.dump(zexus_config, f, indent=2)
        click.echo(f"\nSuccessfully created zexus.json in {os.getcwd()}")
    except Exception as e: click.echo(f"Error: Could not write file. {e}", err=True)

@cli.command()
@click.argument('package_name', required=False)
def install(package_name):
    """Installs a specific package or all dependencies from zexus.json."""
    if package_name:
        install_single_package(package_name)
    else:
        click.echo("Installing dependencies from zexus.json...")
        try:
            with open('zexus.json', 'r') as f: config = json.load(f)
            dependencies = config.get('dependencies', {})
            if not dependencies:
                click.echo("No dependencies found in zexus.json."); return
            for pkg in dependencies: install_single_package(pkg)
        except FileNotFoundError: click.echo("Error: zexus.json not found. Run 'zpm init' first.", err=True)
        except Exception as e: click.echo(f"An error occurred: {e}", err=True)

@cli.command()
@click.argument('script_name')
def run(script_name):
    """Runs a script from your zexus.json file."""
    try:
        with open('zexus.json', 'r') as f: config = json.load(f)
        script = config.get('scripts', {}).get(script_name)
        if not script:
            click.echo(f"Error: Script '{script_name}' not found in zexus.json.", err=True); return
        click.echo(f"> {script}")
        subprocess.run(script, shell=True)
    except FileNotFoundError: click.echo("Error: zexus.json not found.", err=True)
    except Exception as e: click.echo(f"An error occurred: {e}", err=True)

@cli.command()
def test():
    """Runs the 'test' script from your zexus.json file."""
    ctx = click.get_current_context()
    ctx.invoke(run, script_name='test')

@cli.command()
def publish():
    """Publishes your package to the registry (simulation)."""
    try:
        with open('zexus.json', 'r') as f: config = json.load(f)
        name = config.get("name", "Unnamed Package")
        version = config.get("version", "0.0.0")
        click.echo(f"Publishing {name} v{version}...")
        click.echo("Successfully published to the Zexus Registry! (Simulation complete)")
    except FileNotFoundError: click.echo("Error: zexus.json not found. Cannot publish.", err=True)

def install_single_package(package_name):
    click.echo(f"--- Installing '{package_name}' ---")
    if package_name not in REGISTRY:
        click.echo(f"Error: Package '{package_name}' not found.", err=True); return
    modules_dir = "zexus_modules"
    if not os.path.exists(modules_dir): os.makedirs(modules_dir)
    package_path = os.path.join(modules_dir, package_name)
    if os.path.exists(package_path):
        click.echo(f"Package '{package_name}' is already installed."); return
    package_url = REGISTRY[package_name]
    try:
        subprocess.run(["git", "clone", package_url, package_path], check=True, capture_output=True)
        click.echo(f"Successfully installed '{package_name}'.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo(f"Error: Failed to clone package. Make sure git is installed.", err=True); return
    try:
        with open('zexus.json', 'r+') as f:
            config = json.load(f)
            if package_name not in config.get('dependencies', {}):
                config.setdefault('dependencies', {})[package_name] = "1.0.0"
                f.seek(0); json.dump(config, f, indent=2); f.truncate()
                click.echo(f"Updated zexus.json with '{package_name}' dependency.")
    except (FileNotFoundError, KeyError): pass

if __name__ == '__main__':
    cli()
