#!/usr/bin/env python
#
# Author: Scott Sanders <scott@jssjr.com>
#
# Collect statistics from Varnish, format them, and send them to Graphite.

import argparse
import json
import signal
import socket
import string
import subprocess
import time


def parse_varnishstat():
  return json.loads(subprocess.check_output(['varnishstat', '-1', '-j']))


def format_stat(title, metric, timestamp, prefix = None):
  if prefix:
    name = string.join([prefix, title],".") 
  else:
    name = title

  return "{} {} {}".format(name, metric, timestamp)


def report_status(prefix):
  stats  = parse_varnishstat()
  ts     = int(time.time())

  status = []
  # Cache
  status.append(format(format_stat("cache.hit", stats['cache_hit']['value'], ts, prefix)))
  status.append(format(format_stat("cache.hitpass", stats['cache_hitpass']['value'], ts, prefix)))
  status.append(format(format_stat("cache.miss", stats['cache_miss']['value'], ts, prefix)))

  # Origin
  status.append(format(format_stat("backend.conn", stats['backend_conn']['value'], ts, prefix)))
  status.append(format(format_stat("backend.unhealthy", stats['backend_unhealthy']['value'], ts, prefix)))
  status.append(format(format_stat("backend.busy", stats['backend_busy']['value'], ts, prefix)))
  status.append(format(format_stat("backend.fail", stats['backend_fail']['value'], ts, prefix)))
  status.append(format(format_stat("backend.reuse", stats['backend_reuse']['value'], ts, prefix)))
  status.append(format(format_stat("backend.toolate", stats['backend_toolate']['value'], ts, prefix)))
  status.append(format(format_stat("backend.recycle", stats['backend_recycle']['value'], ts, prefix)))
  status.append(format(format_stat("backend.retry", stats['backend_retry']['value'], ts, prefix)))
  status.append(format(format_stat("backend.req", stats['backend_req']['value'], ts, prefix)))

  # Client
  status.append(format(format_stat("client.conn", stats['client_conn']['value'], ts, prefix)))
  status.append(format(format_stat("client.drop", stats['client_drop']['value'], ts, prefix)))
  status.append(format(format_stat("client.req", stats['client_req']['value'], ts, prefix)))
  status.append(format(format_stat("client.hdrbytes", stats['s_hdrbytes']['value'], ts, prefix)))
  status.append(format(format_stat("client.bodybytes", stats['s_bodybytes']['value'], ts, prefix)))

  return status


def main():
  parser = argparse.ArgumentParser(description='Collect and stream Varnish statistics to Graphite.')
  parser.add_argument('-H', '--host', default='127.0.0.1')
  parser.add_argument('-p', '--port', default=2003)
  parser.add_argument('-P', '--prefix', default='varnish')
  # Ethernet - (IPv6 + TCP) = 1500 - (40 + 32) = 1428
  parser.add_argument('-b', '--buffer-size', dest='buffer_size', default=1428)
  args = parser.parse_args()

  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect((args.host, args.port))

  send_buffer = ""

  while True:
    status = report_status(args.prefix)
    for s in status:
      if len(send_buffer) + len(s) > args.buffer_size:
        print "Sending {} bytes to {}".format(len(send_buffer), "{}:{}".format(args.host, args.port))
        client.send(send_buffer)
        send_buffer = ""
      send_buffer += "{}\n".format(s)

    time.sleep(10)

  s.close()

if __name__ == "__main__":
  main()

