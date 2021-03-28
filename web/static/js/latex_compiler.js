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
        // add a duplicate bracket only if its a bracket and its the first one, meaning that 2 brackets will only become
        // 3 and not 4, meaning that we only add 1 for each group of brackets
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
    latex_input = fix_brackets(latex_input);

    // Added Time to force reload on recompilation even if the template did not change
    // we need this, because the user might want to compile again and get different result
    // when using random variables
    let url = '/api/v1/compile_latex?template=' + encodeURIComponent(latex_input) + '&t=' + new Date().getTime();

    if (!img) {
        // create the image for the first time
        img = $('<img src="" alt="LaTeX compiled image display"/>');
        $('#latex_output_container').append(img);
    }
    img.attr('src', url);
}

// this function is used only an input latex is got not from the text input, this can be from the url,
// or from history popState
function compile_latex_and_update_input(latex_input) {
    compile_latex(latex_input);

    code_mirror_editor.getDoc().setValue(latex_input);
}

function compile_latex_input_field() {
    // get the value of the input
    let latex_input = code_mirror_editor.getValue();

    // update the input into the url by using `history.pushState`
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('template', latex_input);

    let new_url = window.location.href.split('?')[0];
    new_url += "?" + urlParams.toString();

    window.history.pushState({template: latex_input}, "", new_url);

    compile_latex(latex_input);
}

function add_latex_input_form_submit_handler() {
    let submit_button = $('#latex_input_submit_button');

    submit_button.on('click', function (event) {
        compile_latex_input_field();
    });
}

function add_history_pop_state_handler() {
    window.onpopstate = function(event) {
        if (event) {
            if (event.state) {
                compile_latex_and_update_input(event.state.template);
            } else {
                // no state, meaning that this is the start, so compile an empty image, another option is to remove
                // the image, but not sure which is best
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

function insert_random_variable(variable_name) {
    code_mirror_editor.replaceSelection(`{{${variable_name}}}`);
    code_mirror_editor.focus();
}

// Add the `CodeMirror` editor
initialize_code_mirror_editor();

// attach handler to the form submit button
add_latex_input_form_submit_handler();

// history pushState
add_history_pop_state_handler();

// if there are params in the search query, then compile and display them
compile_params();
