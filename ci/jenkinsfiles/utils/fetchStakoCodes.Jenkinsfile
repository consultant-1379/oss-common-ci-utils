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

  stages {
    stage("Prepare") {
      steps {
        sh "touch Updated_Stako.xls"
        sh "chmod 777 Updated_Stako.xls"
      }
    }

    stage("Upload File") {
      steps {
        timeout(time: 10, unit: "MINUTES") {
          script {
            def inputFile = input message: "Upload file", parameters: [base64File("FOSS_latest.xls")]
            withEnv(["inputFile=$inputFile"]) {
              sh "echo $inputFile | base64 -d > FOSS_uploaded.xls"
              sh "chmod 777 FOSS_uploaded.xls"
            }
          }
        }
      }
    }

    stage("Write Stako") {
      steps {
        withCredentials([string(credentialsId: 'SCAS_REFRESH_TOKEN', variable: 'SCAS_REFRESH_TOKEN')]) {
          sh 'docker run --rm --volume $(pwd):$(pwd) --env SCAS_REFRESH_TOKEN -v /etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates -w $(pwd) armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-py3kubehelmbuilder:2.2.0-3 bash -c "pip install pandas; pip install glom; pip install xlrd; pip install pip-system-certs; pip install xlwt; which python; pip freeze | grep pandas; python3 -V; python ci/scripts/utils/stakoCodes.py"'
          archiveArtifacts allowEmptyArchive: true, artifacts: "*.xls"
        }
      }
    }
  }
}