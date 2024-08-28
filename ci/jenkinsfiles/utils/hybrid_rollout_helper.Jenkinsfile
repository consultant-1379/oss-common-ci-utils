#!/usr/bin / env groovy

pipeline {
    agent {
        label env.NODE_LABEL
    }

    options {
        timestamps()
        timeout(time: 05, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    environment {
        OUTPUT_DIRECTORY = "build"
        REPORT = "${WORKSPACE}/${env.OUTPUT_DIRECTORY}/output.html"
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    clone_ci_repo()
                }
            }
        }

        stage('Compile EXC List') {
            steps {
                script {
                    compile()
                    archiveArtifacts allowEmptyArchive: true, artifacts: "build/output.html"
                }
            }
        }
    }
}

def clone_ci_repo() {
    sh """
        mkdir -p build/projects/ || true
        [ -d oss-common-ci-utils ] && rm -rf oss-common-ci-utils
        git clone ${GERRIT_MIRROR}/OSS/com.ericsson.oss.ci/oss-common-ci-utils
        cd oss-common-ci-utils
        git checkout dVersion-2.0.0-hybrid
        cp dsl/projects_list_with_jobs_hybrid ../build/projects/
        cp dsl/project_list_with_go_microservices ../build/projects/
        cd ..
        [ -d oss-common-ci-utils ] && rm -rf oss-common-ci-utils
   """
}

def compile() {
    // Read project lists
    def all_projects = []
    def input_file = "${workspace}/build/projects/projects_list_with_jobs_hybrid"
    String input_data = new File(input_file).text
    String[] lines = input_data.split('\n')
    for (String line in lines) {
        if (line.contains("EXC-PCR") || line.contains("EXC-Publish")) {
            all_projects.add(line)
        }
    }

    input_file = "${workspace}/build/projects/project_list_with_go_microservices"
    input_data = new File(input_file).text
    lines = input_data.split('\n')
    for (String line in lines) {
        if (line.contains("EXC-PCR") || line.contains("EXC-Publish")) {
            all_projects.add(line)
        }
    }

    // EXC-PCR
    def data_exc_pcr = []
    for (project in all_projects) {
        if (project.contains("EXC-PCR")) {

            // Jenkins job url
            def jenkins_url = ""
            def job_name = project.split(",")[0].split("/")[2] + "_PreCodeReview_Hybrid"
            if (project.contains("fem1s11")) {
                jenkins_url = "https://fem1s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"
            } else if (project.contains("fem6s11")) {
                jenkins_url = "https://fem6s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"
            } else if (project.contains("fem3s11")) {
                jenkins_url = "https://fem3s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"
            }
            def job_url = "<a href='" + jenkins_url + job_name + "/configure'>" + job_name + "</a>"

            // Project type
            def project_type = ""
            for (value in project.split(",")) {
                if (value.contains("LANG="))
                    project_type = value.toString().replace("LANG=", "")
            }

            // Data
            def data_template = "<tr><td>project_type</td><td>job_url</td><td><input type='checkbox'><label>Done</label></td></tr>"
            def data_string = data_template.replace("project_type", project_type).replace("job_url", job_url)
            data_exc_pcr.add(data_string)
        }
    }

    // EXC-Publish
    def data_exc_publish = []
    for (project in all_projects) {
        if (project.contains("EXC-Publish")) {

            // Jenkins job url
            def jenkins_url = ""
            def job_name = project.split(",")[0].split("/")[2] + "_Publish_Hybrid"
            if (project.contains("fem1s11")) {
                jenkins_url = "https://fem1s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"
            } else if (project.contains("fem6s11")) {
                jenkins_url = "https://fem6s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"
            } else if (project.contains("fem3s11")) {
                jenkins_url = "https://fem3s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"
            }
            def job_url = "<a href='" + jenkins_url + job_name + "/configure'>" + job_name + "</a>"

            // Project type
            def project_type = ""
            for (value in project.split(",")) {
                if (value.contains("LANG="))
                    project_type = value.toString().replace("LANG=", "")
            }

            // Data
            def data_template = "<tr><td>project_type</td><td>job_url</td><td><input type='checkbox'><label>Done</label></td></tr>"
            def data_string = data_template.replace("project_type", project_type).replace("job_url", job_url)
            data_exc_publish.add(data_string)
        }
    }

    data_exc_pcr.sort()
    data_exc_publish.sort()

    // HTML Report
    def html_file = new File("${env.REPORT}")
    def header = "<html><head><style> table, th, td { border: 1px solid rgb(255, 255, 255); border-collapse: collapse; font-size:14px;} th { background: #000; color: #eee; font-weight: bold; padding: 5px; text-align:left;} td { background: #aaa; font-weight: normal; overflow: hidden; padding: 5px; text-overflow: ellipsis; white-space: nowrap; } body { background: #e1e2e3; font-family: sans-serif; font-size:14px;} </style></head>\n<body><b>Hybrid Pipeline Rollout - Checklist</b>"
    def date = String.format('%tF %<tH:%<tM', java.time.LocalDateTime.now())
    html_file.append("${header}")
    html_file.append("<p><b>Report generated on</b>: ${date}</p><br>\n")
    if ("${env.PCR}" == "true") {
        html_file.append("<b>PCR Jobs to be updated manually</b>:<br><br>\n")
        html_file.append("<table><tr><th>Project Type</th><th>Jenkins Job URL</th><th>Rollout Status</th></tr>\n")
        for (data in data_exc_pcr) {
            if (("${env.JAVA}" == "true") && data.contains("Java")) {
                html_file.append(data)
            }
            if (("${env.GO}" == "true") && data.contains("GO")) {
                html_file.append(data)
            }
            if (("${env.OTHER}" == "true") && !(data.contains("GO")) && !(data.contains("Java"))) {
                html_file.append(data)
            }
        }
        html_file.append("</table>\n<br><br>\n")
    }

    if ("${env.PUBLISH}" == "true") {
        html_file.append("<b>Publish Jobs to be updated manually</b>:<br><br>\n")
        html_file.append("<table><tr><th>Project Type</th><th>Jenkins Job URL</th><th>Rollout Status</th></tr>\n")
        for (data in data_exc_publish) {
            if (("${env.JAVA}" == "true") && data.contains("Java")) {
                html_file.append(data)
            }
            if (("${env.GO}" == "true") && data.contains("GO")) {
                html_file.append(data)
            }
            if (("${env.OTHER}" == "true") && !(data.contains("GO")) && !(data.contains("Java"))) {
                html_file.append(data)
            }
        }
        html_file.append("</table>\n<br><br>\n")
    }
    html_file.append("</body></html>\n")
}