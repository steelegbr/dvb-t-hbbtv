requirejs(
    ["logger"],
    function init(logger) {
        logger(LOG_LEVEL_INFO, "From init");
        var appManager = document.getElementById("applicationManager");
        var appObject = appManager.getOwnerApplication(document);
        if (appObject) {
            logger(LOG_LEVEL_INFO, "From HbbTV appObject");
        }
    }
);