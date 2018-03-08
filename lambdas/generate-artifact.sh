#!/bin/bash
HOME_PATH=$(pwd)
ZIPFILE="${HOME_PATH}/lambda.zip"
source $(pwd)/$1/bin/activate
if [[ $? != 0 ]]; then
    exit 1;
fi
pip install -r $VIRTUAL_ENV/requeriments.txt

echo $VIRTUAL_ENV/lib/python3.5/site-packages
rm $ZIPFILE
cd $VIRTUAL_ENV
zip $ZIPFILE *.py
zip -ur $ZIPFILE models


cd $VIRTUAL_ENV/lib/python3.5/site-packages/
zip -ur $ZIPFILE .
deactivate

echo "deploy lambda"

# --endpoint-url=http://localhost:4574 \

cd $HOME_PATH

awslocal lambda \
        create-function --function-name=$1 \
        --runtime=python3.5 \
        --role=lambda_policy \
        --handler=app.lambda_handler \
        --zip-file fileb://lambda.zip

if [[ $? != 0 ]]; then
    echo "Lambda already exists...delete and create again"
    
    awslocal lambda delete-function --function-name=$1
    awslocal lambda \
        create-function --function-name=$1 \
        --runtime=python3.5 \
        --role=lambda_policy \
        --handler=app.lambda_handler \
        --zip-file fileb://lambda.zip
    # echo "Update lambda code only"
    # awslocal lambda \
    #     update-function-code --function-name=$1 \
    #     --zip-file fileb://lambda.zip
fi

awslocal lambda invoke \
            --invocation-type Event \
            --function-name $1 \
            outputfile.txt


rm $ZIPFILE