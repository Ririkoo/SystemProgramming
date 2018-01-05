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
    $('#submit_data').on('click', function (event) {
        text_edior.save();
        bnf_edior.save();
        $.ajax({
            url: "parse",
            method: 'post',
            data: {
                text: $('#text').val(),
                bnf: $('#bnf').val()
            }
        }).done(function (data) {
            let output = $('#output');
            if (data['error'] !== undefined)
                output.html(data['error']);
            else {
                let asm_code = GetAssemblerCode(data);
                output.text(JSON.stringify(data, null, 2));
                drawGraph(data);
                emulator = new Enulator(asm_code);
                let step = $("#step");
                step.off('click');
                step.on('click', function () {
                    emulator.step();
                });
                emulator.generateEmulatorCodeBlock($('#text').val())
            }
        });
    });

    let text_edior = CodeMirror.fromTextArea($('#text')[0], {
        mode: "text/x-csrc",
        styleActiveLine: true,
        matchBrackets: true,
        theme: 'seti',
        lineNumbers: true,
        scrollbarStyle: "simple"

        // value: 'test',
    });

    let bnf_edior = CodeMirror.fromTextArea($('#bnf')[0], {
        styleActiveLine: true,
        lineNumbers: true,
        theme: 'seti',
        mode: 'text/x-ebnf',
        scrollbarStyle: "simple"
//     readOnly:false,
//     value: 'test',
//     mode: "clike",
    });

});

class Enulator {
    constructor(asm_code) {
        this.codes = asm_code;
        this.line_number = 0;
        this.variables = {};
        this.stack = [];
        this.renderVaraibleTable();
        this.result=null;
         $('#return').text('');
    }

    step() {
        if (this.line_number < 0)
            return;
        this.line_number++;
        for (let code of this.codes) {
            if (code.line == this.line_number) {
                this.handleCode(code);
            }
        }
        this.tagLine(this.line_number);
        this.renderVaraibleTable();
    }

    handleCode(code) {
        switch (code.op) {
            case'create':
                this.variables[code.id] = 0;
                break;
            case'push':
                this.stack.push(this.getValue(code.p1));
                break;
            case'pop':
                this.variables[code.id] = this.stack.pop();
                break;
            case'mov':
                this.variables[code.to] = this.getValue(code.p1);
                break;
            case'add':
                this.variables[code.to] = this.getValue(code.p1) + this.getValue(code.p2);
                break;
            case'sub':
                this.variables[code.to] = this.getValue(code.p1) - this.getValue(code.p2);
                break;
            case'mul':
                this.variables[code.to] = this.getValue(code.p1) * this.getValue(code.p2);
                break;
            case'div':
                this.variables[code.to] = this.getValue(code.p1) / this.getValue(code.p2);
                break;
            case'ret':
                this.result = this.getValue(code.p1);
                this.end();
                break;
            default:
                throw new Error('不應該會抵達這裡');
        }
    }

    getValue(p) {
        if (p.type === 'id') {
            return this.variables[p.value]
        } else
            return p.value
    }

    end() {
        this.line_number = -1;
        $('#return').text(this.result);
    }

    renderVaraibleTable() {
        let html = '<table cellpadding="3px" cellspacing="5px" border="1px" ><tr><th>名稱</th><th>內容</th></th>';
        for (let name in this.variables) {
            html += '<tr>';
            html += '<td>' + name + '</td>';
            html += '<td>' + this.variables[name] + '</td>';
            html += '</tr>';

        }
        html += '</table>';
        $('#variableTable').html(html);
    }

    generateEmulatorCodeBlock(code) {
        CodeMirror.runMode(code, "text/x-csrc", $('#emulator_code')[0]);
        let html = '<table>';
        let i = 0;
        for (let line of $('#emulator_code').html().split('\n')) {
            html += '<tr data-line-num="' + ++i + '">';
            html += '<td>' + '　' + '</td>';
            html += '<td>' + i + '</td>';
            html += '<td>' + '&nbsp;' + '</td>';
            html += '<td style="background: limegreen">' + '&nbsp;' + '</td>';
            html += '<td>' + '&nbsp;' + '</td>';
            html += '<td>' + line.replace(/ /g, '&nbsp;&nbsp;') + '</td>';
            html += '</tr>';
        }
        html += '</table>';
        // console.log(html);
        $('#emulator_code').html(html);
    }

    tagLine(line) {
        let emulatorCode = $('#emulator_code');
        emulatorCode.find('tr[data-line-num=' + line + '] >td:first-child').text('>');
        emulatorCode.find('tr[data-line-num!=' + line + '] >td:first-child').text('　');
    }
}
function drawGraph(jsondata){
    var myChart = echarts.init(document.getElementById('visgraph'));
    myChart.clear();
    var tmpStrJson = JSON.stringify(jsondata);
    tmpStrJson = tmpStrJson.replace(/value/g,'name')
    var reJson=JSON.parse(tmpStrJson);
    var option = {
        tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove'
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
function ForEachNode(tree, cb) {
    for (let child of tree.children) {
        if (child.children !== undefined) {
            cb(child);
            ForEachNode(child, cb);
        } else {
            if (child.type === 'number')
                child.value = parseInt(child.value);
            cb(child);
        }
    }
}

function GetAssemblerCode(tree) {
    asm = [];
    asm.push({op: 'create', id: '_temp', line: 1});
    // children
    ForEachNode(tree, function (node) {
        if (node.name === 'STMT')
            ProcessSTMT(node, asm)
    });

    return asm;
}


function ProcessSTMT(node, code) {
    let line = node.children[0].line;
    if (node.children[0].value === 'return') {
        code.push({op: 'ret', p1: {type: node.children[1].type, value: node.children[1].value}, line: line})

    } else if (node.children[1].value === '=') {
        code.push({op: 'create', id: node.children[0].value, line: line});
        code.push({op: 'push', p1: {type: 'id', value: '_temp'}, line: line});
        ProcessEXP(node.children[2], code);
        code.push({op: 'mov', p1: {type: 'id', value: '_temp'}, to: node.children[0].value, line: line});
        code.push({op: 'pop', id: '_temp', line: line});
    }

}

function ProcessEXP(node, code) {
    let line = node.children[0].children[0].line;
    let op = '';
    for (let child of node.children) {
        if (op === '' && child.name === 'ITEM')
            code.push({
                op: 'mov',
                p1: {type: child.children[0].type, value: child.children[0].value},
                to: '_temp',
                line: line
            });
        else if (child.value !== undefined) {
            op = child.value;
        } else {
            switch (op) {
                case '+':
                    code.push({
                        op: 'add',
                        p1: {type: 'id', value: '_temp'},
                        p2: {type: child.children[0].type, value: child.children[0].value},
                        to: '_temp',
                        line: line
                    });
                    break;
                case '-':
                    code.push({
                        op: 'sub',
                        p1: {type: 'id', value: '_temp'},
                        p2: {type: child.children[0].type, value: child.children[0].value},
                        to: '_temp',
                        line: line
                    });
                    break;
                case '*':
                    code.push({
                        op: 'mul',
                        p1: {type: 'id', value: '_temp'},
                        p2: {type: child.children[0].type, value: child.children[0].value},
                        to: '_temp',
                        line: line
                    });
                    break;
                case '/':
                    code.push({
                        op: 'div',
                        p1: {type: 'id', value: '_temp'},
                        p2: {type: child.children[0].type, value: child.children[0].value},
                        to: '_temp',
                        line: line
                    });
                    break;
                default:
                    throw new Error('不應該會抵達這裡');
            }
        }
    }
}
