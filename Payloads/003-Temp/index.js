window.addEventListener("load", init);

function init() {
    var appManager = document.getElementById("applicationManager");
    var appObject = appManager.getOwnerApplication(document);
    if (appObject) {
        appObject.show();
        console.log("Here!");
        var logger = new Logger("002-PortScanner");
        logger.log("Test 123!");
        Logger.show();
    }
}

