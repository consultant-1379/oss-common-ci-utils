#!/usr/bin/env groovy

pipeline {

    agent { label env.NODE_LABEL }

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
    }

    environment {
        SCRIPT_PATH = "ci/scripts/monitoring/monitoring_GE.py"
        ERROR_REPORT = "Error_logs.txt"
        DOCKER_CONFIG_STATUS = "Docker_Config_Status.txt"
    }

    stages {

        stage('Prepare') {
            steps {
                script {
                   sh "python ${env.SCRIPT_PATH} Prepare"
                }
            }
        }

        stage('FEM Connection') {
            when {
                expression { env.FEM_CONNECTION == "true" }
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} FEM_Connection"
                    }
                }
            }
        }

        stage('FEM FileSystem') {
            when {
                expression { env.FEM_FILESYSTEM == "true" }
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} FEM_FileSystem"
                    }
                }
            }
        }

        stage('FEM Password') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} FEM_Password"
                    }
                }
            }
        }

        stage('FEM Docker Config') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        dockerConfigCheck()
                    }
                }
            }
        }

        stage('GE Connection') {
            when {
                expression { env.GE_CONNECTION == "true" }
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} GE_Connection"
                    }
                }
            }
        }

        stage('GE FileSystem') {
            when {
                expression { env.GE_FILESYSTEM == "true" }
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} GE_FileSystem"
                    }
                }
            }
        }

        stage('GE Queue') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} GE_Queue"
                    }
                }
            }
        }

        stage('GE Docker Analysis') {
            when {
                expression { env.GE_DOCKER_ANALYSIS == "true" }
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} GE_DockerSystemAnalysis"
                    }
                }
            }
        }

        stage('GE Docker Containers') {
            when {
                expression { env.GE_DOCKER_CONTAINER == "true" }
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} GE_DockerContainer"
                    }
                }
            }
        }

        stage('GE Docker Images') {
            when {
                expression { env.GE_DOCKER_IMAGE == "true" }
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} GE_DockerImage"
                    }
                }
            }
        }

        stage('GE Docker Volumes') {
            when {
                expression { env.GE_DOCKER_VOLUME == "true" }
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} GE_DockerVolume"
                    }
                }
            }
        }

        stage('GE Docker Networks') {
            when {
                expression { env.GE_DOCKER_NETWORK == "true" }
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} GE_DockerNetwork"
                    }
                }
            }
        }

        stage('GE Docker Build Cache') {
            when {
                expression { env.GE_DOCKER_BUILD_CACHE == "true" }
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} GE_DockerCache"
                    }
                }
            }
        }

        stage('GE Health Check') {
            when {
                expression { env.GE_FILESYSTEM == "true" }
            }
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} PostCleanupCheck"
                    }
                }
            }
        }

        stage('Generate Report') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} GenerateReport"
                    }
                }
            }
        }

        stage('Send Email') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} Email"
                    }
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts allowEmptyArchive: true, artifacts: "${env.ERROR_REPORT}"
            archiveArtifacts allowEmptyArchive: true, artifacts: "FEM_FileSystem_Report.csv"
            archiveArtifacts allowEmptyArchive: true, artifacts: "GE_FileSystem_Report.csv"
            archiveArtifacts allowEmptyArchive: true, artifacts: "GE_Monitoring_Report.html"
            publishHTML (target: [allowMissing: false, alwaysLinkToLastBuild: false, keepAll: true, reportDir: "", reportFiles: "GE_Monitoring_Report.html", reportName: "GE_Monitoring_Report"])
        }
    }
}


def dockerConfigCheck() {
    println("----------------------- Docker Config Check -------------------------")
    sh """
    #!/bin/bash
    if [ -d "/home/ossadmin/.docker" ]
    then
        if cmp -s "/home/ossadmin/.docker/config.json" "/home/ossadmin/.docker/config_backup.json"
        then
            echo "No changes detected in the config.json file"
            echo "true" >> ${env.DOCKER_CONFIG_STATUS}
        else
            echo "The config.json file has changed!"
            echo "false" >> ${env.DOCKER_CONFIG_STATUS}
            echo "Replacing config.json file with the config_backup.json file"
            cp /home/ossadmin/.docker/config_backup.json /home/ossadmin/.docker/config.json
            echo "Docker config changes have been detected! Restored with the backup file." >> ${env.ERROR_REPORT}
        fi
    fi
    echo "Docker Config Check: Success!"
    """

    def status = new File("${WORKSPACE}/${env.DOCKER_CONFIG_STATUS}").text
    if(status.contains("false")) {
        manager.addWarningBadge("Docker config file changes have been detected! Restored with the backup file!")
    }
    println("---------------------------------------------------------------------")
}


