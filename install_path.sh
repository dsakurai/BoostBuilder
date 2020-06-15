#!/usr/bin/env bash
for name in "${1}"/libboost_*.dylib; do
    install_name_tool -id "${name}" ${name}
done

