import redis
from flask import Flask, request, render_template
from rq import Queue
import requests
from tasks import send_request_to_server

app = Flask(__name__)
app.name = "DYNAPHISH_QUEUE_SERVER"

redis_conn = redis.Redis(host="redis", port=6379)
# Create multiple queues
q1 = Queue("has-logo-queue", connection=redis_conn)
q2 = Queue("knowledge-expansion-queue", connection=redis_conn)
q3 = Queue("phishintention-queue", connection=redis_conn)


def is_server_pingable(port):
    try:
        url = f"http://192.168.1.5:{port}"
        response = requests.head(url)
        return 200 <= response.status_code <= 300
    except requests.exceptions.RequestException:
        return False


@app.route("/")
def index():
    data = {
        "has-logo-queue": (len(q1), is_server_pingable(8010)),
        "knowledge-expansion-queue": (len(q2), is_server_pingable(8020)),
        "phishintention-queue": (len(q3), is_server_pingable(8030)),
    }
    return render_template('table.html',data=data)


@app.route("/<string:queue>/<string:folder>", methods=["POST"])
def add_to_queue(queue, folder):
    q_len = 0
    if request.method == "POST":
        if queue == "has-logo-queue":
            job = q1.enqueue(send_request_to_server, 8010, queue, folder)
            q_len = len(q1)

        if queue == "knowledge-expansion-queue":
            job = q2.enqueue(send_request_to_server, 8020, queue, folder)
            q_len = len(q2)

        if queue == "phishintention-queue":
            job = q3.enqueue(send_request_to_server, 8030, queue, folder)
            q_len = len(q3)

        return (
            f"the task {job.id} is added into the task {queue} at {job.enqueued_at}. {q_len} task in queue",
            200,
        )

    return "Request method not found, Only POST is avilable", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
