#!/bin/bash

function pngtoeps {
  for f in ./ja/LC_MESSAGES/*.po; do
    python translate_po.py --lang en $f 1>${f%.po}_en.po
    mv ${f%.po}_en.po $f;
  done; 
}

pngtoeps

