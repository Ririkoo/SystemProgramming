import os

from flask import Flask, request, redirect, url_for, \
    render_template, flash, Markup

import processlib.Tools as Tools
from processlib.Parser import Parser
from processlib.Scanner import Scanner

basedir = os.path.abspath(os.path.dirname(__file__))

# configuration
DEBUG = True
SECRET_KEY = 'mkz75asklLd8wdA9'
# create app
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/parse', methods=['POST'])
def add_entry():
    c0_code = request.form['text']
    parser = Parser(Scanner(c0_code))
    parser_res = Tools.dump_html_code(parser.parsed_tree)
    flash(Markup(parser_res))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
