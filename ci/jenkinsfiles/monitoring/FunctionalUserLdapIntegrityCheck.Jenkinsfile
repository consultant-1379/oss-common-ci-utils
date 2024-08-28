#!/usr/bin/env groovy

pipeline {

    agent {
        node {
            label NODE_LABEL
        }
    }

    options {
        timestamps()
        timeout(time: 5, unit: 'MINUTES')
    }

    stages {
        stage('Init') {
            steps {
                clone_ci_repo()
                pullPatchset()
                sh "bash oss-common-ci-utils/ci/scripts/monitoring/copyFile.sh"

            }
        }
        stage('Functional User integrity check') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python oss-common-ci-utils/ci/scripts/monitoring/FunctionUserLdapIntegrityCheck.py"
                    }
                }
            }
        }
    }
    post {
        always {
            sh '''
            rm -rf ci
            rm -rf emailToSend.html
            rm -rf oss-common-ci-utils
            rm -rf scripts
	    rm -rf jenkins_config_as_code
            scp -r * /home/ossadmin/IDUN_repo/FUldap/
            '''
        }
    }
}

def clone_ci_repo(){
   sh '''
       [ -d oss-common-ci-utils ] && rm -rf oss-common-ci-utils
        git clone ${GERRIT_MIRROR}/OSS/com.ericsson.oss.ci/oss-common-ci-utils
   '''
}
def pullPatchset(){
    if (env.GERRIT_REFSPEC !='' && env.GERRIT_REFSPEC != "refs/heads/master") {
        sh '''
        pwd
        cd oss-common-ci-utils
        pwd
        git fetch ${GERRIT_CENTRAL}/OSS/com.ericsson.oss.ci/oss-common-ci-utils $GERRIT_REFSPEC && git checkout FETCH_HEAD
        '''
    }
}
