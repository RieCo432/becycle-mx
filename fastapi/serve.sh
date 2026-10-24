#!/bin/sh
# Entrypoint for the api service.
#
# Set SEGFAULT_DEBUG=1 (in the api service env) and this runs uvicorn under
# glibc's libSegFault catcher. On the next segfault the container log gets
# a native backtrace naming the library + function that faulted, before the
# process aborts. Needs no core dumps and no host access.
#
# Without SEGFAULT_DEBUG set, this behaves exactly like the old
# `uvicorn app.main:app ...` command.

if [ -n "$SEGFAULT_DEBUG" ]; then
    libsegfault=$(find /usr/lib -name 'libSegFault.so' 2>/dev/null | head -n 1)
    if [ -n "$libsegfault" ]; then
        echo "serve.sh: SEGFAULT_DEBUG=1 - segfault backtraces will be printed to this log"
        export LD_PRELOAD="$libsegfault"
        exec uvicorn app.main:app --host "$API_HOST_ADDRESS" --port "$API_HOST_PORT"
    else
        echo "serve.sh: SEGFAULT_DEBUG=1 but libSegFault.so was not found; running without the fault catcher"
    fi
fi

exec uvicorn app.main:app --host "$API_HOST_ADDRESS" --port "$API_HOST_PORT"
