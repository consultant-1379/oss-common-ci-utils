pipeline {
    agent {
        label env.NODE_LABEL
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    stages {
        stage('Fetch HB Owned Gerrit Repositories') {
            steps {
                script {
                    get_repos()
                    archiveArtifacts allowEmptyArchive: true, artifacts: "output.txt"
                }
            }
        }
    }
}

def get_repos() {
    sh "touch ${workspace}/output.txt"
    def output = new File("${workspace}/output.txt")

    sh "ssh -p 29418 ${env.GERRIT_SERVER} gerrit ls-projects --has-acl-for Aeonic_CI_admin > repo.txt"
    String[] projects = (new File("${workspace}/repo.txt").text).split('\n')
    for (String project in projects) {
        withCredentials([usernamePassword(credentialsId: 'GERRIT_PASSWORD', usernameVariable: 'GERRIT_USER', passwordVariable: 'GERRIT_PASSWORD')]) {
            sh "curl -u '${GERRIT_USER}:${GERRIT_PASSWORD}' -H 'Accept: application/json' https://${env.GERRIT_SERVER}/a/access/?project=${project} -o response.json"
        }

        String response = new File("${workspace}/response.json").text
        if (response.contains('"is_owner":true')) {
            output.append(project + "\n")
        }
        sh "rm -f ${workspace}/response.json"
    }
    sh "rm -f ${workspace}/repo.txt"
}