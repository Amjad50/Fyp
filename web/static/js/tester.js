let input_img_preview;

let segmentation_img;
let classification_img;
let parsing_img;

let input_code_mirror_editor;
let code_mirror_output_latex;

function initialize_code_mirror_editors() {
    code_mirror_output_latex = CodeMirror.fromTextArea(document.getElementById('latex_output_editor'), {
        mode: "stex", theme: "dracula", lineNumbers: true, inMathMode: true, readOnly: true,
    });
    input_code_mirror_editor = CodeMirror.fromTextArea(document.getElementById('latex_input_editor'), {
        mode: "stex", theme: "dracula", lineNumbers: true, inMathMode: true,
        extraKeys: {
            "Ctrl-Enter": function () {
                compile_latex_input_editor();
            }
        }
    });
}

function add_buttons_handlers() {
    $('#compile_and_predict_button').on('click', () => compile_latex_input_editor());
}

function add_history_pop_state_handler() {
    window.onpopstate = function (event) {
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

function compile_latex_and_update_input(latex_input) {
    compile_latex(latex_input);

    input_code_mirror_editor.getDoc().setValue(latex_input);
}

function compile_params() {
    const urlParams = new URLSearchParams(window.location.search);
    const template = urlParams.get('template');

    if (template) {
        compile_latex_and_update_input(template);
    }
}

function insert_random_variable(variable_name) {
    input_code_mirror_editor.replaceSelection(`{{${variable_name}}}`);
    input_code_mirror_editor.focus();
}

function compile_latex_input_editor() {
    // get the value of the input
    let latex_input = input_code_mirror_editor.getValue();

    // update the input into the url by using `history.pushState`
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('template', latex_input);

    let new_url = window.location.href.split('?')[0];
    new_url += "?" + urlParams.toString();

    window.history.pushState({template: latex_input}, "", new_url);

    compile_latex(latex_input);
}

function compile_latex(latex_input) {
    latex_input = fix_brackets(latex_input);

    // Added Time to force reload on recompilation even if the template did not change
    // we need this, because the user might want to compile again and get different result
    // when using random variables
    let url = '/api/v1/compile_latex?template=' + encodeURIComponent(latex_input) + '&t=' + new Date().getTime();

    if (!input_img_preview) {
        // create the image for the first time
        input_img_preview = $('<img src="" alt="LaTeX compiled image display"/>');
        $('#input_img_preview_container').append(input_img_preview);

        input_img_preview.on('error', e => {
            report_error('error in compiling LaTeX due to wrong format or mistyped variable.')
        });
        input_img_preview.on('load', () => run_prediction_for_image());
    }
    input_img_preview.attr('src', url);
}

function run_prediction_for_image() {
    const img_base64 = img_to_base64(input_img_preview[0]);

    // create the segmentation, classification, parsing preview images if they are not created yet (first time)
    if (!segmentation_img) {
        segmentation_img = $('<img src="" class="image-in-card my-2" alt="Segmentation of the input image"/>');
        $('#segmentation_img_container').append(segmentation_img);
    }
    if (!classification_img) {
        classification_img = $('<img src="" class="image-in-card my-2" alt="Classification of symbols in the input image"/>');
        $('#classification_img_container').append(classification_img);
    }
    if (!parsing_img) {
        parsing_img = $('<img src="" class="image-in-card my-2" alt="Parsing tree connections between symbols in the input image"/>');
        $('#parsing_img_container').append(parsing_img);
    }

    // in each step, we would call the API in the first index and assign the result to the image in the second index
    // note that this happen simultaneously meaning we send all requests at once and update the images on callbacks
    let steps = [
        ['draw_image_segments', segmentation_img],
        ['draw_labeled_crops', classification_img],
        ['draw_symbol_tree', parsing_img],
    ];

    for (let step of steps) {
        const api_call = step[0];
        const img_obj = step[1];

        $.ajax({
            url: 'api/v1/' + api_call,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({image: img_base64}),
            xhr: () => { // Seems like the only way to get access to the xhr object and change its type to blob
                let xhr = new XMLHttpRequest();
                xhr.responseType = 'blob'
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 2) {
                        if (xhr.status === 200) {
                            xhr.responseType = "blob";
                        } else {
                            xhr.responseType = "text";
                        }
                    }
                };
                return xhr;
            },
        }).done(function (data) {
            let reader = new FileReader();
            reader.onload = function (event) {
                img_obj.attr('src', event.target.result);
            };
            reader.readAsDataURL(data);
        }).fail(function (ajax_obj, textStatus, errorThrown) {
            report_error(`${api_call} request failed:`, ajax_obj.responseText);
        })
    }

    predict_latex_and_update_output_editor(img_base64);
}

function predict_latex_and_update_output_editor(img_base64) {
    $.ajax({
        url: 'api/v1/predict_latex',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({image: img_base64, optimize: true}),
    }).done(function (data) {
        code_mirror_output_latex.getDoc().setValue(data['latex']);
        // build url to go to `latex_compiler` for the user to compare the two images
        let compile_url = '/latex_compiler';
        compile_url += `?template=${encodeURIComponent(data['latex'])}`;
        $("#compile_output_latex_button").attr('href', compile_url);
    }).fail(function (ajax_obj, textStatus, errorThrown) {
        report_error(`latex prediction:`, ajax_obj.responseText);
    })
}

initialize_code_mirror_editors();
add_buttons_handlers();
add_history_pop_state_handler();
compile_params();
