requirejs(
    ["logger", "scanner"],
    function init(logger, scanner) {
        logger(LOG_LEVEL_INFO, "Init called!");
        var appManager = document.getElementById("applicationManager");
        var appObject = appManager.getOwnerApplication(document);
        if (appObject) {
            scanner('172.16.2.1', 8080, 30).then((res) => {
                let [isOpen, m, sumOpen, sumClosed] = res;
                logger(LOG_LEVEL_INFO, 'Is 172.16.2.1:8080 open? ' + isOpen);
            });
        }
    }
);