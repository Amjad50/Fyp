let code_mirror_editor;
let img;

function initialize_code_mirror_editor() {
    code_mirror_editor = CodeMirror.fromTextArea(document.getElementById('latex_input'), {
        mode: "stex", theme: "dracula", lineNumbers: true, inMathMode: true,
        extraKeys: {
            "Ctrl-Enter": function() {
                compile_latex_input_field();
            }
        }
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


function compile_latex(latex_input) {

    let url = '/api/v1/compile_latex?template=' + encodeURIComponent(latex_input);

    if (!img) {
        img = $('<img src="" alt="LaTeX compiled image display"/>');
        $('#latex_output_container').append(img);
    }
    img.attr('src', url);
}

function compile_latex_and_update_input(latex_input) {
    compile_latex(latex_input);

    code_mirror_editor.getDoc().setValue(latex_input);
}

function compile_latex_input_field() {
    let latex_input = code_mirror_editor.getValue();

    latex_input = fix_brackets(latex_input);

    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('template', latex_input);

    // window.location.search = urlParams.toString();
    let new_url = window.location.href.split('?')[0];
    new_url += "?" + urlParams.toString();

    window.history.pushState({template: latex_input}, "", new_url);

    compile_latex(latex_input);
}

function add_latex_input_form_submit_handler() {
    let form = $('#latex_input_form');

    form.on('submit', function (event) {
        // we don't want to be transferred to another page
        event.preventDefault();

        compile_latex_input_field();
    });
}

function add_history_pop_state_handler() {
    window.onpopstate = function(event) {
        if (event) {
            if (event.state) {
                compile_latex_and_update_input(event.state.template);
            } else {
                // no state, meaning that this it the start
                compile_latex_and_update_input("");
            }
        }
    }
}

function compile_params() {
    const urlParams = new URLSearchParams(window.location.search);
    const template = urlParams.get('template');

    if (template) {
        compile_latex_and_update_input(template);
    }
}

// Add the `CodeMirror` editor
initialize_code_mirror_editor();

// attach handler to the form submit button
add_latex_input_form_submit_handler();

// history pushState
add_history_pop_state_handler();

// if there are params in the search query, then compile and display them
compile_params();
