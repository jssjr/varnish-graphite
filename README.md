# varnish-graphite

Small Python script for sending Varnish statistics to Graphite.

## Usage

```
usage: varnish-graphite [-h] [-H HOST] [-p PORT] [-n NAME] [-P PREFIX]
                        [-i INTERVAL] [-b BUFFER_SIZE] [-B MAX_BUFFER_SIZE]

Collect and stream Varnish statistics to Graphite.

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  The graphite server host (default: 127.0.0.1)
  -p PORT, --port PORT  The graphite server port (default: 2003)
  -n NAME, --name NAME  Specifies the name of the varnishd instance to get
                        logs from. If -n is not specified, the host name is
                        used. (default: albatross-3.local)
  -P PREFIX, --prefix PREFIX
                        The prefix for metric names (default: varnish)
  -i INTERVAL, --interval INTERVAL
                        The collection interval in seconds (default: 10)
  -b BUFFER_SIZE, --buffer-size BUFFER_SIZE
                        The number of bytes to send each time (default: 1428)
  -B MAX_BUFFER_SIZE, --max-buffer-size MAX_BUFFER_SIZE
                        The maximum number of bytes to buffer when
                        reconnecting (default: 33554432)
```
