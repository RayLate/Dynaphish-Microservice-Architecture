
import re
import certstream
import math
import tqdm
import yaml
import time
import os
from Levenshtein import distance
from termcolor import colored, cprint
from tld import get_tld
import socket
from confusables import unconfuse
# from certstream import CertStreamClient

# Introducing argparse to add arguments for date seen for particular certificate
# Usually, phishing websites last for approximate 54 hours = 2.25 days
import argparse
import time

certstream_url = 'wss://certstream.calidog.io'

log_suspicious = os.path.dirname(os.path.realpath(__file__))+'/suspicious_domains_'+time.strftime("%Y-%m-%d")+'.log'

suspicious_yaml = os.path.dirname(os.path.realpath(__file__))+'/suspicious.yaml'

external_yaml = os.path.dirname(os.path.realpath(__file__))+'/external.yaml'

pbar = tqdm.tqdm(desc='certificate_update', unit='cert')
connection = None

def entropy(string):
    """Calculates the Shannon entropy of a string"""
    prob = [ float(string.count(c)) / len(string) for c in dict.fromkeys(list(string)) ]
    entropy = - sum([ p * math.log(p) / math.log(2.0) for p in prob ])
    return entropy

def convert_days_to_unix(days):
    return days * 86400

def score_domain(domain):
    """Score `domain`.

    The highest score, the most probable `domain` is a phishing site.

    Args:
        domain (str): the domain to check.

    Returns:
        int: the score of `domain`.
    """
    score = 0
    for t in suspicious['tlds']: # tld is in suspicious tld list, increase suspiciousness score
        if domain.endswith(t):
            score += 20 

    # Remove initial '*.' for wildcard certificates bug
    if domain.startswith('*.'):
        domain = domain[2:]

    # Removing TLD to catch inner TLD in subdomain (ie. paypal.com.domain.com)
    try:
        res = get_tld(domain, as_object=True, fail_silently=True, fix_protocol=True)
        domain = '.'.join([res.subdomain, res.domain])
    except Exception:
        pass

    # Higer entropy is kind of suspicious
    score += int(round(entropy(domain)*10))

    # Remove lookalike characters using list from http://www.unicode.org/reports/tr39
    domain = unconfuse(domain)

    words_in_domain = re.split("\W+", domain)

    # ie. detect fake .com (ie. *.com-account-management.info)
    if words_in_domain[0] in ['com', 'net', 'org']:
        score += 10

    # Testing keywords
    for word in suspicious['keywords']:
        if word in domain:
            score += suspicious['keywords'][word]

    # Testing Levenshtein distance for strong keywords (>= 70 points) (ie. paypol)
    for key in [k for (k,s) in suspicious['keywords'].items() if s >= 70]:
        # Removing too generic keywords (ie. mail.domain.com)
        for word in [w for w in words_in_domain if w not in ['email', 'mail', 'cloud']]:
            if distance(str(word), str(key)) == 1:
                score += 70

    # Lots of '-' (ie. www.paypal-datacenter.com-acccount-alert.com)
    if 'xn--' not in domain and domain.count('-') >= 4:
        score += domain.count('-') * 3

    # Deeply nested subdomains (ie. www.paypal.com.security.accountupdate.gq)
    if domain.count('.') >= 3:
        score += domain.count('.') * 3

    return score


def callback(message, context):
    # Need to hardcode the recency here, due to API callback
    days = 1.00
    cert_recency = time.time() - convert_days_to_unix(float(1.00))

    """Callback handler for certstream events."""
    if message['message_type'] == "heartbeat":
        return
    # moderate speed of callbacks
    time.sleep(0.02)

    # Introducing the idea of cert recency
    if message['message_type'] == "certificate_update" and message['data']['seen'] > cert_recency:
        all_domains = message['data']['leaf_cert']['all_domains']

        for domain in all_domains:
            pbar.update(1)
            score = score_domain(domain.lower())
            # If issued from a free CA = more suspicious

            if score > 40: # set score threshold here
                global connection

                connection.send(domain.encode('utf-8'))
                if os.path.exists(log_suspicious):
                    existing = set(filter(None, set(open(log_suspicious,'r').read().split('\n'))))
                    with open(log_suspicious, 'a') as f:
                        if domain not in existing:
                            f.write("{}\n".format(domain))
                else:
                    with open(log_suspicious, 'a') as f:
                        f.write("{}\n".format(domain))
                        tqdm.tqdm.write("[!] Suspicious: ""{} (score={})".format(domain, score))

                return domain


if __name__ == '__main__':
    SERVER = "localhost"
    PORT = 8889
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((SERVER, PORT))
    print("connected")
    with open(suspicious_yaml, 'r') as f:
        suspicious = yaml.safe_load(f)

    with open(external_yaml, 'r') as f:
        external = yaml.safe_load(f)

    if external['override_suspicious.yaml'] is True:
        suspicious = external
    else:
        if external['keywords'] is not None:
            suspicious['keywords'].update(external['keywords'])

        if external['tlds'] is not None:
            suspicious['tlds'].update(external['tlds'])

    certstream.listen_for_events(callback, url=certstream_url)

