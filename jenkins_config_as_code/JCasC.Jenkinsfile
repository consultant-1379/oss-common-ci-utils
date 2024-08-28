#!/usr/bin/env groovy

pipeline {

    agent { label 'GridEngine' }

    options {
        timestamps()
    }

    stages {
        stage('Prepare') {
            steps {
                fetchPass()
            }
        }
        
        stage('Plugin install') {
            steps {
                sh '''
                    if [ "$PLUGIN_FILE_NAME" ]
                    then 
                        echo "It is not empty!"
                        echo plugin_file = "$PLUGIN_FILE_NAME"
                        bash jenkins_config_as_code/scripts/installPlugin.sh $DESTINATION_FEM_SERVER $PLUGIN_FILE_NAME
                    fi
                '''
            }
        }
        stage('JCasC reload') {
            steps {
                sh '''
                    if [ "$CONFIG_FILE_NAME" ]
                    then 
                        echo "It is not empty!"
                        echo CONFIG_FILE_NAME = "$CONFIG_FILE_NAME"
                        bash jenkins_config_as_code/scripts/reload_JCaaC.sh $DESTINATION_FEM_SERVER $CONFIG_FILE_NAME
                    fi
                '''
            }
        }
        stage('Restart') {
            steps {
                sh '''
                    if [ "$RESTART_FEM" == "Yes" ]
                    then 
                        echo "going to restart fem"
                        bash jenkins_config_as_code/scripts/restart.sh $DESTINATION_FEM_SERVER $RESTART_FEM
                    fi
                '''
            }
        }
        
    }
    post {
        always {
            sh '''
                rm -rf secret
            '''
        }
    }
}


def fetchPass() {
    withCredentials([usernamePassword(credentialsId: 'GERRIT_PASSWORD', passwordVariable: 'PASSWORD', usernameVariable: 'user')]) {
    sh 'echo $PASSWORD > secret'
    }
}
