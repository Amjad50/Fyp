function fix_brackets(latex_input) {
    latex_input =  latex_input.replace(/{{([^{}]*)}}/g, "\u1234$1\u1235");

    let output = "";
    for (let c of latex_input) {
        if (c === '\u1234')
            output += '{{{'
        else if (c === '\u1235')
            output += '}}}'
        else
            output += c;

        if ((c === '}' || c === '{') ) {
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

