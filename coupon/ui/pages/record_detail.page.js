/**
 * Created by Nitori on 2017/5/4.
 */

export default () => {
    $('#submit-btn').click((e) => {
        const telAlert = $('.illegal-tel-alert');
        if (!($('#tel-input').val().match(/^1[34578]\d{9}$/))) {
            telAlert.show();
            e.preventDefault();
        } else {
            telAlert.hide();
        }
    });
};
