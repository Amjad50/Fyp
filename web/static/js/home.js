let input_img_preview;

let segmentation_img;
let classification_img;
let parsing_img;

let code_mirror_output_latex;

function add_input_image_change_handler() {
    $("#equation_img_file_input").on('change', function (event) {
        const files = event.target.files;
        if (!files)
            return;

        if (files.length < 1) {
            // the file was removed or no file was chosen, so lets remove the image
            // remove all children
            $("#input_img_preview_container").empty();
        } else {
            const img_file = files[0];


            if (!input_img_preview) {
                input_img_preview = $('<img src="" class="image-in-card my-2" alt="Mathematical expression input image preview"/>');
                $('#input_img_preview_container').append(input_img_preview);
            }

            const reader = new FileReader();
            reader.addEventListener('load', event => {
                input_img_preview.attr('src', event.target.result);
            });
            reader.readAsDataURL(img_file);
        }
    });
}

function predict_latex_and_update_output_preview(img_base64) {
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
        console.error(`predict_latex request failed`, textStatus, errorThrown)
    })
}

function run_prediction_for_image() {
    // get the image base64 from the preview img src
    const whole_img_data = input_img_preview.attr('src');
    const base64_split = whole_img_data.split(';')[1];

    // make sure it is base64
    if (!base64_split.startsWith('base64,')) {
        console.error("Could not read base64 from input image preview, stopping prediction...");
        return;
    }

    // remove the `base64,` prefix
    const img_base64 = base64_split.slice('base64,'.length);

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
                xhr.responseType= 'blob'
                return xhr;
            },
        }).done(function (data) {
            let reader = new FileReader();
            reader.onload = function(event){
                img_obj.attr('src', event.target.result);
            };
            reader.readAsDataURL(data);
        }).fail(function (ajax_obj, textStatus, errorThrown) {
            console.error(`${api_call} request failed`, textStatus, errorThrown)
        })
    }

    predict_latex_and_update_output_preview(img_base64);
}

function add_image_submit_handler() {
    let form = $('#equation_img_input_form');

    form.on('submit', function (event) {
        // we don't want to be transferred to another page
        event.preventDefault();

        run_prediction_for_image();
    });
}

function initialize_code_mirror_output_preview() {
    code_mirror_output_latex = CodeMirror.fromTextArea(document.getElementById('latex_output'), {
        mode: "stex", theme: "dracula", lineNumbers: true, inMathMode: true, readOnly: true,
    });
}

add_input_image_change_handler();

add_image_submit_handler();

// Add the `CodeMirror` editor to the output LaTeX preview
initialize_code_mirror_output_preview();
