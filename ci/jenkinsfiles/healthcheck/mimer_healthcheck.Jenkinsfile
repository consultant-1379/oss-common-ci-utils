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
        stage('Mimer') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'GERRIT_PASSWORD', usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        sh "python ci/scripts/healthchecks/url_access_checker.py 'Mimer' 'https://mimer.internal.ericsson.com/'"
                    }
                }
            }
        }
    }
}