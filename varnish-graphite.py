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


class GraphiteClient:
  sendbuf = ''

  def __init__(self, host='127.0.0.1', port=2003, prefix='varnish', buffer_size=1428):
    self.prefix = prefix
    self.host   = host
    self.port   = port
    self.buffer_size = buffer_size

    self.connect()

  def connect(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((self.host, self.port))
    print("Connected to {}:{}".format(self.host, self.port))

  def send_metrics(self, metrics):
    for stat in metrics:
      if len(self.sendbuf) + len("{}.{}".format(self.prefix, stat)) > self.buffer_size:
        print("Sending {} bytes to {}".format(len(self.sendbuf), "{}:{}".format(self.host, self.port)))
        self.sock.send(self.sendbuf)
        self.sendbuf = ''
      self.sendbuf += "{}.{}\n".format(self.prefix, stat)

  def disconnect(self):
    self.sock.close()
    print("Disconnected from {}:{}".format(self.host, self.port))


def parse_varnishstat():
  return json.loads(subprocess.check_output(['varnishstat', '-1', '-j']))


def collect_metrics():
  stats  = parse_varnishstat()
  ts     = int(time.time())

  status = []
  fmt = lambda x, y, z: "{} {} {}".format(x, stats[y]['value'], ts)

  # Cache
  status.append(fmt('cache.hit', 'cache_hit', ts))
  status.append(fmt('cache.hitpass', 'cache_hitpass', ts))
  status.append(fmt('cache.miss', 'cache_miss', ts))

  # Origin
  status.append(fmt('backend.conn', 'backend_conn', ts))
  status.append(fmt('backend.unhealthy', 'backend_unhealthy', ts))
  status.append(fmt('backend.busy', 'backend_busy', ts))
  status.append(fmt('backend.fail', 'backend_fail', ts))
  status.append(fmt('backend.reuse', 'backend_reuse', ts))
  status.append(fmt('backend.toolate', 'backend_toolate', ts))
  status.append(fmt('backend.recycle', 'backend_recycle', ts))
  status.append(fmt('backend.retry', 'backend_retry', ts))
  status.append(fmt('backend.req', 'backend_req', ts))

  # Client
  status.append(fmt('client.conn', 'client_conn', ts))
  status.append(fmt('client.drop', 'client_drop', ts))
  status.append(fmt('client.req', 'client_req', ts))
  status.append(fmt('client.hdrbytes', 's_hdrbytes', ts))
  status.append(fmt('client.bodybytes', 's_bodybytes', ts))

  return status


def main():
  parser = argparse.ArgumentParser(description='Collect and stream Varnish statistics to Graphite.')
  parser.add_argument('-H', '--host', default='127.0.0.1')
  parser.add_argument('-p', '--port', default=2003)
  parser.add_argument('-P', '--prefix', default='varnish')
  # Ethernet - (IPv6 + TCP) = 1500 - (40 + 32) = 1428
  parser.add_argument('-b', '--buffer-size', dest='buffer_size', default=1428)
  args = parser.parse_args()

  c = GraphiteClient(args.host, args.port, args.prefix)

  send_buffer = ""

  try:
    while True:
      c.send_metrics(collect_metrics())
      time.sleep(10)
  except KeyboardInterrupt:
    c.disconnect();

if __name__ == "__main__":
  main()

