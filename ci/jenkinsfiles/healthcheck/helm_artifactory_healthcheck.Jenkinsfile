#!/usr/bin/env groovy

pipeline {
    agent {
        node {
            label env.NODE_LABEL
        }
    }

    options {
        timestamps()
        timeout(time: 5, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    stages {
        stage('Helm Artifactory') {
           environment {
                JOB_NAME = "${env.JOB_NAME}"
                BUILD_URL = "${env.BUILD_URL}"
                DOCKER_IMAGE = "armdocker.rnd.ericsson.se/proj-eric-oss-drop/oss-common-ci-utils/eric-oss-common-ci-python:latest"
                SCRIPT = "ci/scripts/healthchecks/url_access_checker.py"
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                       withCredentials([usernamePassword(credentialsId: 'GERRIT_PASSWORD', usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                            sh '''
                                docker run\
                                --rm\
                                --workdir $(pwd)\
                                --user "$(id -u):$(id -g)"\
                                --volume $(pwd):$(pwd)\
                                --env GERRIT_USERNAME\
                                --env GERRIT_PASSWORD\
                                --env JOB_NAME\
                                --env BUILD_URL\
                                --env EMAIL\
                                --env REQUEST_TIMEOUT\
                                ${DOCKER_IMAGE}\
                                bash -c "python -u ${SCRIPT} 'Helm Artifactory (dev)' 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-dev-helm-local/'"
                                bash -c "python -u ${SCRIPT} 'Helm Artifactory (ci-internal)' 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-ci-internal-helm-local/'"
                                bash -c "python -u ${SCRIPT} 'Helm Artifactory (drop)' 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local/'"
                                bash -c "python -u ${SCRIPT} 'Helm Artifactory (release)' 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-released-helm-local/'"
                                bash -c "python -u ${SCRIPT} 'Helm Artifactory (testware)' 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-ci-drop-testware-helm-local/'"
                            '''
                       }
                    }
                }
            }
        }
    }
}