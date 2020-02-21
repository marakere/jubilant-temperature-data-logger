#!/usr/bin/bash

# $1 - project-dir
# $2 - api-name
# $3 - env-name


PROJECT_SRC=${PWD%/*}
PROJECT_SRC=${PROJECT_SRC}/src
API_NAME=$1
ENV_TYPE=$2
ENV_NAME=$3

echo $PROJECT_SRC

# By default - dev will be assigned
ENV_NAME=${ENV_NAME:=dev}
APP_NAME=recordtemperature
ASSET_BUCKET=REPLACE_WITH_AWS_BUCKETNAME

BUILD_DIR=${API_NAME}/build

function copy_project_dependencies() {
	requirement=${API_NAME}/requirements.txt
	if [ -f "$requirement" ]; then
		echo "Installting packages into build directory"
		pip install -r $requirement --upgrade -t $BUILD_DIR/
	fi
	cp -r  ${API_NAME}/*.py $BUILD_DIR/
	rsync -av --progress ${API_NAME}/** $BUILD_DIR/ --exclude build
}

function deploy_to_aws() {
	cd ${API_NAME}
	sam package --output-template-file packaged.yaml --s3-bucket $ASSET_BUCKET --s3-prefix serverless_lambda_package/${API_NAME}
	STACK_NAME=$(echo "${API_NAME}" | sed -r 's/(^|_)([a-z])/\L\2/g')
	STACK_NAME=${APP_NAME}-${ENV_NAME}-${STACK_NAME}
	echo $STACK_NAME
	aws cloudformation deploy --template-file packaged.yaml --parameter-overrides EnvName=${ENV_NAME} AppName=${APP_NAME} --stack-name ${STACK_NAME}  --capabilities CAPABILITY_NAMED_IAM --region us-east-1
}

echo "Removing the existing build source and creating a new one"
rm -r  $BUILD_DIR && mkdir -p $BUILD_DIR

# Invoke a method to install python dependencies and copy the required project source
copy_project_dependencies

if [ "${ENV_TYPE}" == "local" ]; then
    cd ${API_NAME} && sam local start-api
elif [ "${ENV_TYPE}" == "aws" ]; then
	deploy_to_aws
fi
