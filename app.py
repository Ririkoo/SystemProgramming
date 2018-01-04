import os
import traceback

from flask import Flask, request, redirect, url_for, \
    render_template, flash, Markup

import processlib.Tools as Tools
from processlib.Parser import BNFParser, c0_ebnf
from processlib.Scanner import BNFScanner
from processlib.SemanticAnalyser import SemanticAnalyser
from processlib.Tools import TreeTools

basedir = os.path.abspath(os.path.dirname(__file__))

# configuration
DEBUG = True
SECRET_KEY = 'mkz75asklLd8wdA9'
# create app
app = Flask(__name__)
app.config.from_object(__name__)


# parser
# SAnalyser = SemanticAnalyser(BNFParser(c0_ebnf, 'PROG', BNFScanner()))


# SAnalyser = SemanticAnalyser(Parser(Scanner()))
bnf_rules = c0_ebnf

@app.route('/')
def index():
    flash(bnf_rules, 'bnf_editor')
    return render_template('index.html')


@app.route('/parse', methods=['POST'])
def add_entry():
    global bnf_rules
    c0_code = request.form['text']
    bnf_rules = request.form['bnf'].strip() or c0_ebnf
    # flash(bnf_rules, 'bnf_editor')
    s_analyser = SemanticAnalyser(BNFParser(bnf_rules, 'PROG', BNFScanner()))
    try:
        flash(c0_code, 'editor')

        parser_res = TreeTools.dump_html_code(s_analyser.parse(c0_code))
        flash(Markup(parser_res), 'output')
    except Exception as e:
        flash(Markup(Tools.dump_to_html(str(e))), 'output')
        traceback.print_exc()
    finally:
        return redirect(url_for('index'))


if __name__ == '__main__':
    # Remote Debug
    app.run(host='localhost', port=5000)
