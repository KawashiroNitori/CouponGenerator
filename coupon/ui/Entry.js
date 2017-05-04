/**
 * Created by Nitori on 2017/5/2.
 */
import 'normalize.css/normalize.css';
import 'bootstrap';

async function main() {
    const pages = require.context('../', true, /\.page\.js$/i);
    const pageInstances = pages.keys().map(key => pages(key).default);
    for (const func of pageInstances) {
        await func();
    }
    $('[data-toggle="tooltip"]').tooltip();
}

main();
