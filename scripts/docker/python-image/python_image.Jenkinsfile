#!/usr/bin/env groovy

def ruleset = "scripts/docker/python-image/python_image_ruleset.yaml"
def bob = "python3 bob/bob.py -r ${ruleset}"

@Library("oss-common-pipeline-lib@dVersion-2.0.0-hybrid") _
pipeline {
    agent {
        label env.NODE_LABEL
    }

    options {
        timestamps()
        timeout(time: 15, unit: "MINUTES")
        buildDiscarder(logRotator(numToKeepStr: "15", artifactNumToKeepStr: "15"))
    }

    stages {
        stage("Prepare") {
            steps {
                deleteDir()
                script {
                    ci_pipeline_init.clone_project()
                    ci_pipeline_init.setBuildName()
                }
                sh "git submodule add ../../../adp-cicd/bob"
                sh "${bob} --help"
                sh "${bob} -lq"
            }
        }

        stage("Init") {
            steps {
                script {
                    sh "${bob} init"
                }
            }
        }

        stage("Build") {
            environment {
                DOCKER_IMAGE = get_parameters('DOCKER_IMAGE')
                DOCKER_FILE = get_parameters('DOCKER_FILE')
            }
            steps {
                script {
                    sh "docker build -t ${DOCKER_IMAGE} -f ${DOCKER_FILE} ."
                    sh '''
                    docker run\
                        --rm\
                        --workdir $(pwd)\
                        --user "$(id -u):$(id -g)"\
                        --volume $(pwd):$(pwd)\
                        ${DOCKER_IMAGE}\
                        bash -c "python --version > build/python_version.txt;pip freeze > build/pip_requirements.txt"
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts allowEmptyArchive: true, artifacts: "build/python_version.txt"
                    archiveArtifacts allowEmptyArchive: true, artifacts: "build/pip_requirements.txt"
                }
            }
        }

        stage("Lint") {
            environment {
                DOCKER_IMAGE = get_parameters('DOCKER_IMAGE')
                TESTS = get_parameters('TESTS')
            }
            steps {
                parallel(
                    "Hadolint": {
                        sh "${bob} hadolint-scan"
                    },
                    "Image DR Check": {
                        script {
                            ci_pipeline_scripts.retryMechanism("${bob} image-dr-check", 3)
                        }
                    },
                    "Pylint": {
                        sh '''
                        docker run\
                            --rm\
                            --workdir $(pwd)\
                            --user "$(id -u):$(id -g)"\
                            --volume $(pwd):$(pwd)\
                            ${DOCKER_IMAGE}\
                            bash -c "pylint --output=build/pylint_output.txt ${TESTS}; exit 0;"
                        '''
                    },
                    "Flake": {
                        sh '''
                        docker run\
                            --rm\
                            --workdir $(pwd)\
                            --user "$(id -u):$(id -g)"\
                            --volume $(pwd):$(pwd)\
                            ${DOCKER_IMAGE}\
                            bash -c "flake8 --config=scripts/docker/python-image/.flake8 --output=build/flake8_output.txt ${TESTS}; exit 0;"
                        '''
                    }
                )
            }
            post {
                always {
                    archiveArtifacts allowEmptyArchive: true, artifacts: "build/hadolint-reports/*.txt"
                    archiveArtifacts allowEmptyArchive: true, artifacts: "build/image-dr-check/*.html"
                    archiveArtifacts allowEmptyArchive: true, artifacts: "build/pylint_output.txt"
                    archiveArtifacts allowEmptyArchive: true, artifacts: "build/flake8_output.txt"
                }
            }
        }

        stage('Test') {
            environment {
                DOCKER_IMAGE = get_parameters('DOCKER_IMAGE')
                TESTS = get_parameters('TESTS')
                JOB_URL = "${env.JOB_URL}"
            }
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'GERRIT_PASSWORD',
                        usernameVariable: 'GERRIT_USERNAME',
                        passwordVariable: 'GERRIT_PASSWORD')
                ]) {
                    sh '''
                    docker run\
                        --rm\
                        --workdir $(pwd)\
                        --user "$(id -u):$(id -g)"\
                        --volume $(pwd):$(pwd)\
                        --env GERRIT_USERNAME\
                        --env GERRIT_PASSWORD\
                        --env JOB_URL\
                        ${DOCKER_IMAGE}\
                        bash -c "python -u ${TESTS}"
                    '''
                }
            }
        }

        stage('Publish') {
            environment {
                DOCKER_IMAGE = get_parameters('DOCKER_IMAGE')
            }
            steps {
                sh "${bob} publish"
            }
        }

        stage("Cleanup") {
            environment {
                DOCKER_IMAGE = get_parameters('DOCKER_IMAGE')
            }
            steps {
                sh "${bob} cleanup"
            }
        }
    }
    post {
        success {
            set_build_description()
        }
        unsuccessful {
            send_email()
        }
    }
}

String get_parameters(String param) {
    if (param.isEmpty()) {
        return ' '
    }
    switch (param) {
    case 'DOCKER_IMAGE':
        return "armdocker.rnd.ericsson.se/proj-eric-oss-drop/oss-common-ci-utils/eric-oss-common-ci-python:${env.IMAGE_VERSION}"
    case 'DOCKER_FILE':
        return "scripts/docker/python-image/python_image.dockerfile"
    case 'TESTS':
        return "scripts/docker/python-image/python_image_tests.py"
    default:
        break
    }
}

def send_email() {
    try {
        mail to: "${env.EMAIL}",
            from: "jenkins-ossadmin-no-reply@ericsson.com",
            cc: "",
            subject: "Action Required! Failure in ${env.JOB_NAME}",
            body: "The build <a href='${env.BUILD_URL}'>#${env.BUILD_NUMBER}</a> of ${env.JOB_NAME} has failed!<br>" +
            "Please have a look into this and take appropriate action!<br>" +
            "<br><b>Note</b>: This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>",
            mimeType: "text/html"
    } catch (Exception e) {
        echo "Email notification was not sent!"
        print e
    }
}

def set_build_description() {
    def version = readFile("build/python_version.txt").trim()
    currentBuild.description = "<b>Python version: </b>${version}"
}