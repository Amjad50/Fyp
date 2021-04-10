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

function img_to_base64(img) {
    const canvas = document.createElement("canvas");
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);
    const dataURL = canvas.toDataURL("image/png");

    return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
}

