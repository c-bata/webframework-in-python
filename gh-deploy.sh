#!/bin/bash

echo "* gh-pages ブランチを削除します"
git branch -D gh-pages

echo "* gh-pages ブランチを作成してcheckoutします"
git checkout -b gh-pages

echo "* sphinxをbuildしてrootに展開します"
cd docs/
make html
cd ..
cp -r docs/build/html .

echo "* slidesをrootに展開します"
cp -r slides/ .

echo "git pushします"
git add .
git commit -m "Deploy gh-pages"
git push -f origin gh-pages

echo "* masterブランチに戻ります"
git checkout master
