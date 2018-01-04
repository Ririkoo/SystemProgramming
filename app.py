import os
import traceback

from flask import Flask, request, redirect, url_for, \
    render_template, flash, Markup, jsonify

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

default_code = '''sum = 0;
for (i=1; i<=9; i++)
{
  for (j=1; j<=9; j++)
  {
    p = i * j;
    sum = sum + p;
  }
}

return sum;
'''


@app.route('/')
def index():
    flash(c0_ebnf, 'bnf_editor')
    flash(default_code, 'editor')
    return render_template('index.html')


@app.route('/parse', methods=['POST'])
def add_entry():
    global bnf_rules
    c0_code = request.form['text']
    bnf_rules = request.form['bnf'].strip() or c0_ebnf
    s_analyser = SemanticAnalyser(BNFParser(bnf_rules, 'PROG', BNFScanner()))
    try:
        parser_res = TreeTools.dump_html_code(s_analyser.parse(c0_code))
        return jsonify(parser_res)

    except Exception as e:
        return jsonify(Tools.dump_to_html(str(e)))
        traceback.print_exc()


if __name__ == '__main__':
    # Remote Debug
    app.run(host='localhost', port=5000)
