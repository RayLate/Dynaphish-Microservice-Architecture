#!/bin/sh
/bin/sh -ec 'python server.py &'
/bin/sh -ec 'sleep 5 && python catch_phishing_certstream.py'
/bin/sh -ec 'sleep 5 && python catch_phishing.py'