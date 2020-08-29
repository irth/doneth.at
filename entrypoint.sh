#!/bin/bash
chown -R www-data:www-data /data
flask db upgrade && gosu www-data "$@"

