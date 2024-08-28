#!/usr/bin / env groovy

pipeline {
  agent {
    label env.NODE_LABEL
  }

  options {
    timestamps()
    timeout(time: 15, unit: "MINUTES")
    buildDiscarder(logRotator(numToKeepStr: "15", artifactNumToKeepStr: "15"))
  }

  environment {
    SCRIPT = 'ci/scripts/utils/refreshScasOfflineToken.py'
  }

  stages {
    stage("Refresh Offline Token") {
      steps {
        catchError(stageResult: 'FAILURE') {
          script {
            withCredentials([string(credentialsId: 'SCAS_REFRESH_TOKEN', variable: 'SCAS_REFRESH_TOKEN')]) {
              sh "python ${env.SCRIPT} refreshScasOfflineToken"
            }
          }
        }
      }
    }
  }
}