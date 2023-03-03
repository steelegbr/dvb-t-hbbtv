window.addEventListener("load", init);

function init() {
    console.log("Here!");
    var logger = new Logger("002-PortScanner");
    logger.log("Test 123!");
    Logger.show();
}

