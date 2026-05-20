#!/bin/sh
set -e

mkdir -p /app/data
chown -R routeforge:routeforge /app/data

exec gosu routeforge "$@"
