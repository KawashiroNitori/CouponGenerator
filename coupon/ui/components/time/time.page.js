import Timeago from 'timeago.js';

function runRelativeTime($container) {
    $container.find('span.time.relative[data-timestamp]').get().forEach((element) => {
        const $element = $(element);
        if ($element.data('timeago') !== undefined) {
            return;
        }
        const timeago = new Timeago();
        timeago.setLocale('zh_CN');
        $element.attr('data-title', $element.text());
        $element.attr('data-toggle', $element.text());
        $element.attr('data-animation', 'false');
        $element.attr('datetime', ($element.attr('data-timestamp') || 0) * 1000);
        timeago.render(element);
        $element.data('timeago', timeago);
    });
}

function cancelRelativeTime($container) {
    $container.find('span.time.relative[data-timestamp]').get().forEach((element) => {
        const $element = $(element);
        const timeago = $element.data('timeago');
        if (timeago === undefined) {
            return;
        }
        timeago.cancel();
        $element.removeData('timeago');
    });
}

const relativeTimePage = () => {
    runRelativeTime($('body'));
    $(document).on('ContentNew', e => runRelativeTime($(e.target)));
    $(document).on('ContentRemove', e => cancelRelativeTime($(e.target)));
};

export default relativeTimePage;
