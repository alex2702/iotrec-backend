// disable all categories on level 0 (Root) or level 1
document.onreadystatechange = () => {
    /* in category selects, disable top-level categories */
    if (document.readyState === 'complete') {
        [].forEach.call(document.querySelectorAll('#id_categories option'), function(elm) {
            if(!elm.innerText.startsWith('------')) {
                elm.disabled = true;
            }
        })
    }
};
