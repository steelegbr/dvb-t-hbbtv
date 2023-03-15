const BASE_URL = location.hostname == "localhost" ? "http://localhost:8000/" : "/";
const LOG_LEVEL_INFO = "Info";
const LOG_LEVEL_ERROR = "Error";

define(
    ["https://cdnjs.cloudflare.com/ajax/libs/uuid/8.3.2/uuid.min.js"],
    function (uuid) {
        const session_id = uuid.v4();

        return function (level, message) {
            const log_url = `${BASE_URL}api/log/${session_id}`;
            fetch(
                log_url,
                {
                    method: "POST",
                    body: JSON.stringify(
                        {
                            level: level,
                            entry: message
                        }
                    ),
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );
        }
    }
);

