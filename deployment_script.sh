#!/bin/zsh

rm -f -r ./package
rm -f deployment-package.zip
pip3.12 install --no-dependencies --target ./package -r requirements.txt
pip3.12 install git+https://github.com/NYPL/python-utils.git@qa-v1.2.0 --target ./package
cd package
zip -r ../deployment-package.zip .
cd ..
zip deployment-package.zip lambda_function.py
zip deployment-package.zip record_processor.py