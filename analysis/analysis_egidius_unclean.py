#!/usr/bin/env python3

import json
import matplotlib.pyplot as plt


def tranco_pages():
    with open("../tranco-top-500-safe.csv") as f:
        f.readline()
        lines = f.readlines()

    ret = []
    for line in lines:
        line = line.strip().split(",")
        num = int(line[0])
        site = line[1]
        ret += [
            [num, site],
        ]
    return ret


def page_json(url):
    accept_json = url + "_accept.json"
    noop_json = url + "_noop.json"
    try:
        with open("../crawl_data/" + accept_json) as f:
            accept_data = json.load(f)
    except Exception:
        accept_data = {}
    try:
        with open("../crawl_data/" + noop_json) as f:
            noop_data = json.load(f)
    except Exception:
        noop_data = {}
    return (accept_data, noop_data)


# string to int, with None = 0
def jint(i):
    if i:
        return int(i)
    else:
        return 0


# 1
def sum_errors():
    a_timeout = 0
    a_dns = 0
    a_consent = 0
    n_timeout = 0
    n_dns = 0
    n_consent = 0
    for num, page in tranco_pages():
        try:
            accept, noop = [x["errors"] for x in page_json(page)]
            a_timeout += jint(accept["page_load_timeout"])
            n_timeout += jint(noop["page_load_timeout"])
            a_dns += jint(accept["dns"])
            n_dns += jint(noop["dns"])
            a_consent += jint(accept["consent_click"])
            n_consent += jint(noop["consent_click"])
        except Exception:
            pass
    print(f"{a_timeout}, {a_dns}, {a_consent}, {n_timeout}, {n_dns}, {n_consent}")


# 5
def trackers_vs_rank():
    a_ranks = []
    a_trackers = []
    n_ranks = []
    n_trackers = []
    for num, page in tranco_pages():
        try:
            accept, noop = [x["tracker_domains"] for x in page_json(page)]
            a_ranks += [
                num,
            ]
            a_trackers += [
                len(accept),
            ]
            n_ranks += [
                num,
            ]
            n_trackers += [
                len(noop),
            ]
        except Exception:
            pass
    plt.scatter(a_ranks, a_trackers, c="red", label="Accept")
    plt.scatter(n_ranks, n_trackers, c="green", label="Noop")
    plt.title("Tracker domains vs. Tranco rank")
    plt.xlabel("Tranco rank")
    plt.ylabel("Number of distinct tracker domains")
    plt.legend()
    plt.show()


# 6
def tracker_entities():
    a_trackers = {}
    n_trackers = {}
    for num, page in tranco_pages():
        try:
            accept, noop = [x["tracker_entities"] for x in page_json(page)]
            for tracker in accept:
                a_trackers[tracker] = a_trackers.get(tracker, 0) + 1
            for tracker in noop:
                n_trackers[tracker] = n_trackers.get(tracker, 0) + 1

        except Exception:
            pass
    print(sorted(a_trackers.items(), key=lambda item: item[1])[-10:])
    print(sorted(n_trackers.items(), key=lambda item: item[1])[-10:])


# 7
def longest_cookie():
    a_cookies = []
    n_cookies = []
    for num, page in tranco_pages():
        try:
            accept, noop = [x["cookies"] for x in page_json(page)]
            a_cookies += accept
            n_cookies += noop
        except Exception:
            pass
    # There doesn't seem to be a single cookie with max-age
    print(sorted(a_cookies, key=lambda item: item.get("expiry", 0))[-3:])
    print(sorted(n_cookies, key=lambda item: item.get("expiry", 0))[-3:])


# 8
def most_cookies():
    a_most = []
    n_most = []
    for num, page in tranco_pages():
        try:
            accept, noop = [x["cookies"] for x in page_json(page)]
            a_most += [
                (page, len(accept)),
            ]
            n_most += [
                (page, len(noop)),
            ]
        except Exception:
            pass
    print(sorted(a_most, key=lambda item: item[1])[-3:])
    print(sorted(n_most, key=lambda item: item[1])[-3:])


# 9
def redirects():
    a_pairs = {}
    n_pairs = {}
    for num, page in tranco_pages():
        try:
            accept, noop = [x["x_domain_redirects"] for x in page_json(page)]
            for pair in accept:
                pair = pair[0] + " -> " + pair[1]
                a_pairs[pair] = a_pairs.get(pair, 0) + 1
            for pair in noop:
                pair = pair[0] + " -> " + pair[1]
                n_pairs[pair] = n_pairs.get(pair, 0) + 1
        except Exception:
            pass
    print(sorted(a_pairs.items(), key=lambda item: item[1])[-10:])
    print(sorted(n_pairs.items(), key=lambda item: item[1])[-10:])


trackers_vs_rank()
