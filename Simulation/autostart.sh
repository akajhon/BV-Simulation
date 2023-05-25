#!/bin/bash

set -e

host="$1"
shift
cmd="$@"

until nc -z "$host" 5672; do
  >&2 echo -e "\033[31m[!] RabbitMQ is unavailable -> Sleeping... [!]\033[0m"
  sleep 1
done

>&2 echo -e "\033[32m[!] RabbitMQ is up -> Executing Command... [!]\033[0m"
exec $cmd