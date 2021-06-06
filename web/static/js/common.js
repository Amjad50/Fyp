const TOAST_DISAPPEAR_KEY = 'toast_disappear_setting_key';
let toast_disappear_setting;

function fix_brackets(latex_input) {
    latex_input = latex_input.replace(/{{([^{}]*)}}/g, "\u1234$1\u1235");

    let output = "";
    for (let c of latex_input) {
        if (c === '\u1234')
            output += '{{{'
        else if (c === '\u1235')
            output += '}}}'
        else
            output += c;

        if ((c === '}' || c === '{')) {
            output += c;
        }
    }

    return output;
}

function img_to_base64(img) {
    const canvas = document.createElement("canvas");
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);
    const dataURL = canvas.toDataURL("image/png");

    return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
}

function refresh_toast_disappear_setting() {
    toast_disappear_setting = localStorage.getItem(TOAST_DISAPPEAR_KEY) === 'true';
}

function report_error(err_msg_prefix, err) {
    console.error('report_error', err_msg_prefix, err);
    let error_msg = ''
    if (err) {
        try {
            let err_json = JSON.parse(err)

            if (err_json['error']) {
                error_msg = err_json['error'];
            }
        } catch (e) {
            error_msg = err;
        }
    }
    error_msg = err_msg_prefix + ' ' + error_msg;
    let close_button = '';
    if (!toast_disappear_setting) {
        close_button =
            `<button type="button" class="toast_close btn-close btn-close-white" data-bs-dismiss="toast"
        aria-label="Close"></button>`
    }
    let new_toast = $(`
    <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
       <div class="toast-header bg-danger text-white">
         <strong class="me-auto">LaTeX Predictor Error</strong>
         ${close_button}
       </div>
       <div class="toast-body">
         ${error_msg}
       </div>
     </div>
    `);

    if (toast_disappear_setting) {
        const FULL_TIME = 1000;
        const STEPS = 20;
        setTimeout(() => {
            let op = 1;
            setInterval((n) => {
                new_toast.css('opacity', op);
                op -= 1 / STEPS;
                if (op < 0.0) {
                    new_toast.remove();
                }
            }, FULL_TIME / STEPS)
        }, 3000);
    }

    $('#toast_container').append(new_toast);
}

(function load() {
    $(document).ready(function () {
        console.log('ww');
        $('#toast_container').on('click', '.toast_close', function () {
            $(this).closest('.toast').remove();
        })
        refresh_toast_disappear_setting();
    });
})();

