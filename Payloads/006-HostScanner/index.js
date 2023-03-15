requirejs(
    ["logger", "scanner"],
    function init(logger, scanner) {
        logger(LOG_LEVEL_INFO, "Init called!");
        var appManager = document.getElementById("applicationManager");
        var appObject = appManager.getOwnerApplication(document);
        if (appObject) {
            scanPortRange("172.16.2.1", 0, scanner, logger);
        }
    }
);

const MAX_PORT = 65535;
const SKIP_PORT = 37857;

function scanPortRange(server, port, scanner, logger) {
    if (port == SKIP_PORT) {
        scanPort(server, port + 1, scanner);
    }

    if (port >= MAX_PORT) {
        return;
    }

    scanner(server, port, 30).then((res) => {
        let [isOpen, m, sumOpen, sumClosed] = res;
        if (isOpen) {
            logger(LOG_LEVEL_INFO, `Port 172.16.2.1:${port} is open!!!`);
        }
        scanPort(server, port + 1, scanner);
    });
}