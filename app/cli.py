import os
import click

from app import app


@app.cli.group()
def translate():
    """
    Command line operation for pages content translation.
    Subcommands available: update, commit, init {language}
    """

    pass


@translate.command()
def update():
    """Updates all project's languages"""

    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')


@translate.command()
def compile():
    """Compiles translation changes"""

    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')


@translate.command()
@click.argument('lang')
def init(lang):
    """Initializes new language"""

    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')
