(function load() {
    $(document).ready(function () {
        refresh_toast_disappear_setting();

        let toast_disappear_check = $('#toast_disappear_check');
        let toast_disappear_check_test_btn = $('#toast_disappear_check_test');
        if (toast_disappear_setting) {
            toast_disappear_check.prop('checked', toast_disappear_setting);
        } else {
            localStorage.setItem(TOAST_DISAPPEAR_KEY, 'false');
        }
        toast_disappear_check.on('change', (event) => {
            let new_value = event.target.checked.toString();
            localStorage.setItem(TOAST_DISAPPEAR_KEY, new_value);
            refresh_toast_disappear_setting();
        });
        toast_disappear_check_test_btn.on('click', () => {
            report_error('Test error:', 'error message');
        });
    });
})();
