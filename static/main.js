$(function () {

    console.log("ready!"); // sanity check

    $('.entry').on('click', function () {
        let entry = this;
        let post_id = $(this).find('h2').attr('id');
        console.log(post_id);
        $.ajax({
            type: 'GET',
            url: '/delete' + '/' + post_id,
            context: entry,
            success: function (result) {
                if (result.status === 1) {
                    $(this).remove();
                    console.log(result);
                }
            }
        });
    });

    let codes = {
        'for2': `sum = 0;
for (i=1; i<=9; i++)
{
  for (j=1; j<=9; j++)
  {
    p = i * j;
    sum = sum + p;
  }
}
return sum;`
        , 'simple': `a = 1;
b = 2;
c = a + b;
return c;`
        , 'square_sum': `sum = 0;
for (i=0; i<=10; i++)
{
  p = i * i;
  sum = sum + p;
};
return sum;
`
    };

    let rules = {
        'basic': `PROG = BaseList
BaseList = (BASE)*
BASE = FOR | STMT ';'
FOR = 'for' '(' STMT ';' COND ';' STMT ')' BLOCK
STMT = 'return' id | id ('=' EXP |  ('++'|'--'))
BLOCK = '{' BaseList '}'
EXP = ITEM ([+\\-*/] ITEM)?
COND = EXP ('=='|'!='|'<='|'>='|'<'|'>') EXP
ITEM = id | number
id = [A-Za-z_][A-Za-z0-9_]*
number = [0-9]+`,
        'improved1': `PROG = BaseList
BaseList = (BASE)*
BASE = FOR | STMT ';'
FOR = 'for' '(' STMT ';' COND ';' STMT ')' BLOCK
STMT = 'return' id | id ('=' EXP |  ('++'|'--'))
BLOCK = '{' BaseList '}'
EXP = ITEM ([+\\-*/] ITEM)*
COND = EXP ('=='|'!='|'<='|'>='|'<'|'>') EXP
ITEM = id | number | string
id = [A-Za-z_][A-Za-z0-9_]*
number = [0-9]+
string = '"' [A-Za-z0-9_]* '"'`,
        'improved2': `PROG = BaseList
BaseList = (BASE)*
BASE = FOR | STMT END 
END = ';'
FOR = 'for' '(' STMT END  COND END  STMT ')' BLOCK
STMT = 'return' id | id ('=' EXP | UnaryOP))
UnaryOP =  '++'|'--'
BLOCK = '{' BaseList '}'
EXP = ITEM (OP  ITEM)*
OP = [+\\-*/]
COND = EXP CondOP EXP
CondOP = '=='|'!='|'<='|'>='|'<'|'>'
ITEM = id | number | string
id = [A-Za-z_][A-Za-z0-9_]*
number = [0-9]+
string = '"' [A-Za-z0-9_]* '"'
`
    };

    $('#code_select').on('change', function () {
        text_editor.getDoc().setValue(codes[$(this).val()]);
    });


    $('#bnf_select').on('change', function () {
        bnf_editor.getDoc().setValue(rules[$(this).val()]);
    });

    let interval = null;
    let $autoStep = $("#autostep");
    let $step = $("#step");

    let text_editor = CodeMirror.fromTextArea($('#text')[0], {
        mode: "text/x-csrc",
        styleActiveLine: true,
        matchBrackets: true,
        theme: 'seti',
        lineNumbers: true,
        scrollbarStyle: "simple"
    });

    let bnf_editor = CodeMirror.fromTextArea($('#bnf')[0], {
        styleActiveLine: true,
        lineNumbers: true,
        theme: 'seti',
        mode: 'text/x-ebnf',
        scrollbarStyle: "simple"
    });

    $('#submit_data').on('click', function () {
        if (interval !== null) {
            clearInterval(interval);
            $autoStep.val('autostep disable');
            interval = null;
        }
        text_editor.save();
        bnf_editor.save();
        $.ajax({
            url: "parse",
            method: 'post',
            data: {
                text: $('#text').val(),
                bnf: $('#bnf').val()
            }
        }).done(function (data) {
            let output = $('#output');
            let error = $('#error');
            if (data['error'] !== undefined) {
                error.html(data['error']);
                error.show();
                output.html('');
            } else {
                error.html('');
                error.hide();
                drawGraph(data);
                output.text(JSON.stringify(data, null, 2));
                let asm_code = ASMGenerator.getAssemblerCode(data);
                ASMGenerator.renderASMTable(asm_code, $('#asm_code'));
                output.text(output.text());


                let emulator = new Emulator(asm_code);

                $step.off('click');
                $step.on('click', function () {
                    emulator.step();
                });

                $autoStep.off('click');

                $autoStep.on('click', function () {
                    if (interval !== null) {
                        clearInterval(interval);
                        $(this).val('autostep disable');
                        interval = null;
                        return;
                    }
                    interval = setInterval(function () {
                        emulator.step();
                    }, parseInt($('#autostep_interval').val()));
                    $(this).val('autostep enable')
                });


                Emulator.renderEmulatorCodeBlock($('#text').val())
            }
        });
    });


    function drawGraph(jsondata) {
        let myChart = echarts.init(document.getElementById('visgraph'));
        myChart.clear();
        let tmpStrJson = JSON.stringify(jsondata);
        tmpStrJson = tmpStrJson.replace(/value/g, 'name');
        let reJson = JSON.parse(tmpStrJson);
        let option = {
            tooltip: {
                trigger: 'item',
                triggerOn: 'mousemove',
                formatter: function (data) {
                    data = data.data;
                    return '<b>' + data.name + '</b><br/>' + (data.type !== undefined ?
                        ((data.type ? ('type:' + JSON.stringify(data.type) + '<br>') : '') +
                            (data.name ? ('value:' + JSON.stringify(data.name) + '<br>') : '') +
                            (data.kind ? ('kind:' + JSON.stringify(data.kind) + '<br>') : ''))
                        : '');
                }
            },
            series: [{
                type: 'tree',
                data: [reJson],
                top: '1%',
                left: '7%',
                bottom: '1%',
                right: '20%',
                symbolSize: 7,
                label: {
                    normal: {
                        position: 'left',
                        verticalAlign: 'middle',
                        align: 'right',
                        fontSize: 9
                    }
                },
                leaves: {
                    label: {
                        normal: {
                            position: 'right',
                            verticalAlign: 'middle',
                            align: 'left'
                        }
                    }
                },
                expandAndCollapse: true,
                animationDuration: 550,
                animationDurationUpdate: 750
            }]
        };
        myChart.setOption(option);
    }


    class ASMGenerator {

        static getAssemblerCode(tree) {
            let asm = [];
            asm.push({op: 'create', id: '[temp]', line: 1});
            // children
            ASMGenerator._forEachNode(tree, ASMGenerator._handleCodeProcess(asm));

            for (let i = 0; i < asm.length; i++) {
                asm[i].index = i;
            }
            return asm;
        }

        static tagAsmRow(index, next_index, branch_index) {
            let $emulatorCode = $('#asm_code');
            $emulatorCode.find('tr[data-asm-index!=' + index + '] ').removeClass('table-success');
            $emulatorCode.find('tr[data-asm-index=' + index + '] ').addClass('table-success');

            $emulatorCode.find('tr[data-asm-index!=' + branch_index + '] ').removeClass('table-warning');
            $emulatorCode.find('tr[data-asm-index!=' + next_index + '] ').removeClass('table-warning');
            $emulatorCode.find('tr[data-asm-index=' + next_index + '] ').addClass('table-warning');
            $emulatorCode.find('tr[data-asm-index=' + branch_index + '] ').addClass('table-warning');

        }


        static renderASMTable(asm, dom) {
            let html = '<tr><th>Index</th><th>OP</th><th>P1</th><th>P2</th><th>ID</th><th>TO</th></tr>';
            for (let code of asm) {
                html += '<tr data-asm-index="' + code.index + '">';
                html += '<td>' + ASMGenerator._normalize(code.index) + '</td>';
                html += '<td>' + ASMGenerator._normalize(code.op) + '</td>';
                html += '<td>' + ASMGenerator._normalize(code.p1) + '</td>';
                html += '<td>' + ASMGenerator._normalize(code.p2) + '</td>';
                html += '<td>' + ASMGenerator._normalize(code.id) + '</td>';
                html += '<td>' + ASMGenerator._normalize(code.to) + '</td>';
                html += '</tr>';

            }
            $(dom).html(html);
        }

        static _normalize(obj) {
            if (obj === undefined)
                return 'x';
            return JSON.stringify(obj);
        }

        static _handleCodeProcess(asm) {
            return function (node) {
                if (node.name === 'STMT') {
                    ASMGenerator._processSTMT(node, asm);
                    return true;
                } else if (node.name === 'FOR') {
                    ASMGenerator._processFor(node, asm);
                    return true;
                }
                return false;
            }

        }

        static _forEachNode(tree, cb) {
            for (let child of tree.children) {
                if (child.children !== undefined) {
                    let result = cb(child);
                    if (!result)
                        ASMGenerator._forEachNode(child, cb);
                } else {
                    if (child.type === 'number')
                        child.value = parseInt(child.value);
                    cb(child);
                }
            }
        }

        static _processSTMT(node, code) {
            let line = node.children[0].line;
            if (node.children[0].value === 'return') {
                code.push({op: 'ret', p1: {type: node.children[1].type, value: node.children[1].value}, line: line})

            } else if (node.children[1].value === '=') {
                code.push({op: 'create', id: node.children[0].value, line: line});
                code.push({op: 'push', id: '[temp]', line: line});
                ASMGenerator._processEXP(node.children[2], code);
                code.push({op: 'mov', p1: {type: 'id', value: '[temp]'}, to: node.children[0].value, line: line});
                code.push({op: 'pop', id: '[temp]', line: line});
            } else {
                if (node.children[1].value === '++')
                    code.push({
                        op: 'add',
                        p1: {type: 'id', value: node.children[0].value},
                        p2: {type: 'number', value: 1},
                        to: node.children[0].value,
                        line: line
                    })
            }

        }

        static _processFor(node, code) {
            let line = node.children[0].line;
            ASMGenerator._processSTMT(node.children[2], code);
            let cond_point = code.length;
            ASMGenerator._processCOND(node.children[4], code);
            code[code.length - 1].to = code.length + 1;


            let jmp = {op: 'jmp', to: null, line: line};
            code.push(jmp);

            ASMGenerator._forEachNode(node.children[8], ASMGenerator._handleCodeProcess(code));
            ASMGenerator._processSTMT(node.children[6], code);
            code.push({op: 'jmp', to: cond_point, line: line});
            jmp.to = code.length;


        }

        static _processCOND(node, code) {
            let line = node.children[1].line;
            code.push({op: 'push', id: '[temp]', line: line});
            ASMGenerator._processEXP(node.children[0], code);

            code.push({op: 'push', id: '[temp]', line: line});
            ASMGenerator._processEXP(node.children[2], code);
            code.push({op: 'create', id: '[temp2]', line: line});
            code.push({
                op: 'mov',
                p1: {type: 'id', value: '[temp]'},
                to: '[temp2]',
                line: line
            });
            code.push({op: 'pop', id: '[temp]', line: line});
            code.push({
                op: 'cmp',
                p1: {type: 'id', value: '[temp]'},
                p2: {type: 'id', value: '[temp2]'},
                line: line
            });
            code.push({op: 'pop', id: '[temp]', line: line});
            switch (node.children[1].value) {
                case '==':
                    code.push({op: 'jeq', to: null, line: line});
                    break;
                case '!=':
                    code.push({op: 'jne', to: null, line: line});
                    break;
                case '>=':
                    code.push({op: 'jbe', to: null, line: line});
                    break;
                case '<=':
                    code.push({op: 'jle', to: null, line: line});
                    break;
                case '>':
                    code.push({op: 'jb', to: null, line: line});
                    break;
                case '<':
                    code.push({op: 'jl', to: null, line: line});
                    break;
                default:
                    throw new Error('不應該會抵達這裡');
            }

        }


        static _processEXP(node, code) {
            let line = node.children[0].children[0].line;
            let op = '';
            for (let child of node.children) {
                if (op === '' && child.name === 'ITEM')
                    code.push({
                        op: 'mov',
                        p1: {type: child.children[0].type, value: child.children[0].value},
                        to: '[temp]',
                        line: line
                    });
                else if (child.value !== undefined) {
                    op = child.value;
                } else {
                    switch (op) {
                        case '+':
                            code.push({
                                op: 'add',
                                p1: {type: 'id', value: '[temp]'},
                                p2: {type: child.children[0].type, value: child.children[0].value},
                                to: '[temp]',
                                line: line
                            });
                            break;
                        case '-':
                            code.push({
                                op: 'sub',
                                p1: {type: 'id', value: '[temp]'},
                                p2: {type: child.children[0].type, value: child.children[0].value},
                                to: '[temp]',
                                line: line
                            });
                            break;
                        case '*':
                            code.push({
                                op: 'mul',
                                p1: {type: 'id', value: '[temp]'},
                                p2: {type: child.children[0].type, value: child.children[0].value},
                                to: '[temp]',
                                line: line
                            });
                            break;
                        case '/':
                            code.push({
                                op: 'div',
                                p1: {type: 'id', value: '[temp]'},
                                p2: {type: child.children[0].type, value: child.children[0].value},
                                to: '[temp]',
                                line: line
                            });
                            break;
                        default:
                            throw new Error('不應該會抵達這裡');
                    }
                }
            }
        }
    }


    class Emulator {
        constructor(asm_code) {
            this.codes = asm_code;
            this.line_number = 0;
            this.variables = {};
            this.stack = {};
            this.result = null;
            this.compareResult = 0;
            this.asm_index = 0;

            this.renderVariableTable();
            $('#return').text('');
        }

        step() {
            if (this.line_number < 0)
                return;
            // let code = this.codes[this.asm_index];
            // this.line_number = code.line;
            let firstFlag = true;
            while (true) {
                // console.log(this.asm_index);
                let code = this.codes[this.asm_index];

                if (code === undefined) {
                    this._end();
                    return;
                }
                if (firstFlag) {
                    this.line_number = code.line;
                    firstFlag = false;
                }
                if (code.line !== this.line_number)
                    break;

                let current_index = this.asm_index++;
                let next_index = this.asm_index;
                this._handleCode(code);
                ASMGenerator.tagAsmRow(current_index, next_index, this.asm_index);
                if ($('#step_on_asm').prop('checked'))
                    break;
            }
            Emulator.tagLine(this.line_number);
            this.renderVariableTable();
        }

        _handleCode(code) {
            switch (code.op) {
                case'create':
                    if (this.variables[code.id] === undefined)
                        this.variables[code.id] = 0;
                    break;
                case'push':
                    if (this.stack[code.id] === undefined)
                        this.stack[code.id] = [];
                    this.stack[code.id].push(this.variables[code.id]);
                    break;
                case'pop':
                    this.variables[code.id] = this.stack[code.id].pop();
                    break;
                case'mov':
                    this.variables[code.to] = this._getValue(code.p1);
                    break;
                case'add':
                    this.variables[code.to] = this._getValue(code.p1) + this._getValue(code.p2);
                    break;
                case'sub':
                    this.variables[code.to] = this._getValue(code.p1) - this._getValue(code.p2);
                    break;
                case'mul':
                    this.variables[code.to] = this._getValue(code.p1) * this._getValue(code.p2);
                    break;
                case'div':
                    this.variables[code.to] = this._getValue(code.p1) / this._getValue(code.p2);
                    break;
                case'ret':
                    this.result = this._getValue(code.p1);
                    this._end();
                    break;
                case 'cmp':
                    this.compareResult = this._getValue(code.p1) - this._getValue(code.p2);
                    break;
                case 'jmp':
                    this.asm_index = code.to;
                    break;
                case 'jeq'://'=='
                    if (this.compareResult === 0)
                        this.asm_index = code.to;
                    break;
                case 'jne'://'!='
                    if (this.compareResult !== 0)
                        this.asm_index = code.to;
                    break;
                case 'jb'://'>'
                    if (this.compareResult > 0)
                        this.asm_index = code.to;
                    break;
                case 'jl'://'<'
                    if (this.compareResult < 0)
                        this.asm_index = code.to;
                    break;
                case 'jbe'://'>='
                    if (this.compareResult > 0 || this.compareResult === 0)
                        this.asm_index = code.to;
                    break;
                case 'jle'://'<='
                    if (this.compareResult < 0 || this.compareResult === 0)
                        this.asm_index = code.to;
                    break;
                default:
                    throw new Error('不應該會抵達這裡');
            }
        }

        _getValue(p) {
            if (p.type === 'id') {
                return this.variables[p.value]
            } else if (p.type === 'number') {
                return parseFloat(p.value);
            } else
                return p.value
        }

        _end() {
            $('#return').text(this.result);
            // this.line_number = -1;
            Emulator.tagLine(this.line_number);
            this.renderVariableTable();
        }

        renderVariableTable() {
            let html = '<table class="table table-bordered table-sm"><tr><th>名稱</th><th>內容</th></th>';
            for (let name in this.variables) {
                html += '<tr>';
                html += '<td>' + name + '</td>';
                html += '<td>' + this.variables[name] + '</td>';
                html += '</tr>';

            }
            html += '<tr><td>[compareResult]</td><td>' + this.compareResult + '</td></tr>';
            html += '</table>';
            $('#variableTable').html(html);
        }

        static renderEmulatorCodeBlock(code) {
            let $emulatorCode = $('#emulator_code');
            CodeMirror.runMode(code, "text/x-csrc", $emulatorCode[0]);
            let html = '<table width="100%">';
            let i = 0;
            for (let line of $emulatorCode.html().split('\n')) {
                html += '<tr data-line-num="' + ++i + '">';
                html += '<td>' + i + '</td>';
                html += '<td style="background:limegreen"></td>';
                html += '<td>&nbsp;&nbsp;' + line.replace(/ /g, '&nbsp;&nbsp;') + '</td>';
                html += '</tr>';
            }
            html += '</table>';
            // console.log(html);
            $emulatorCode.html(html);
        }

        static tagLine(line) {
            let $emulatorCode = $('#emulator_code');
            // $emulatorCode.find('tr[data-line-num=' + line + '] >td:first-child').text('>');
            // $emulatorCode.find('tr[data-line-num!=' + line + '] >td:first-child').text('　');
            $emulatorCode.find('tr[data-line-num!=' + line + '] ').removeClass('table-success');
            $emulatorCode.find('tr[data-line-num=' + line + '] ').addClass('table-success');
        }
    }
});
