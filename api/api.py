from context import bgchof
import flask
from datetime import date, datetime

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route("/", methods=["GET"])
def home():
    return "<h1>Bulgarian Christian Orthodox Fasting</h1><p>This site is a prototype API for bgchof project.</p>"


# a route to return the message for a specific date
@app.route("/api/v1/msgForDate", methods=["GET"])
def api_msgForDate():
    if "date" in flask.request.args:
        # test if supplied arg is a date
        try:
            theDate = date.fromisoformat(flask.request.args["date"])
            return (
                "<h1>Fasting Diet For "
                + date.isoformat(theDate)
                + "</h1><p>"
                + str(bgchof.getFastingStatusForDate(theDate))
                + "</p>"
            )
        except ValueError:
            return "<h1>Value Error:</h1><p>Please supply a date argument in yyyy-mm-dd format!</p>"
    # elif: #define other input cases
    else:
        theDate = date.today()
        return (
            "<h1>Fasting Diet For "
            + date.isoformat(theDate)
            + "</h1><p>"
            + str(bgchof.getFastingStatusForDate(theDate))
            + "</p>"
        )


# a route to return the value for a specific date

app.run()
