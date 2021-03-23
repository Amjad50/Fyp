function initialize_code_mirror_editor() {
    CodeMirror.fromTextArea(document.getElementById('latex_input'), {
        mode: "stex", theme: "dracula", lineNumbers: true, inMathMode: true,
    });
}

function fix_brackets(latex_input) {
    let output = "";
    let just_encountered_bracket = null;
    for (let c of latex_input) {
        output += c;
        if ((c === '}' || c === '{') && just_encountered_bracket !== c) {
            output += c;
            just_encountered_bracket = c;
        } else {
            just_encountered_bracket = null;
        }
    }

    return output;
}

let img;
function add_latex_input_form_submit_handler() {
    let form = $('#latex_input_form');

    form.on('submit', function (event) {
        // we don't want to be transferred to another page
        event.preventDefault();

        let latex_input = $('#latex_input')[0].value;

        latex_input = fix_brackets(latex_input);

        let url = '/api/v1/compile_latex?template=' + encodeURIComponent(latex_input);

        if (!img) {
            img = $('<img src="" alt="LaTeX compiled image display"/>');
            $('#latex_output_container').append(img);
        }
        img.attr('src', url);
    });
}

// Add the `CodeMirror` editor
initialize_code_mirror_editor();

// attach handler to the form submit button
add_latex_input_form_submit_handler();
