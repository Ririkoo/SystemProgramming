$(function () {

    console.log("ready!"); // sanity check

    $('.entry').on('click', function () {
        var entry = this;
        var post_id = $(this).find('h2').attr('id');
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
            if (data['error'] !== undefined)
                $('#output').html(data['error']);
            else
                $('#output').text(JSON.stringify(data, null, 2))
        });
    });

    var text_edior = CodeMirror.fromTextArea($('#text')[0], {
        mode: "text/x-csrc",
        styleActiveLine: true,
        matchBrackets: true,
        theme: 'seti',
        lineNumbers: true

        // value: 'test',
    });

    var bnf_edior = CodeMirror.fromTextArea($('#bnf')[0], {
        styleActiveLine: true,
        lineNumbers: true,
        theme: 'seti',
        mode: 'text/x-ebnf'
//     readOnly:false,
//     value: 'test',
//     mode: "clike",
    });

});

