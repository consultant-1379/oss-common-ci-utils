#!/usr/bin/env groovy

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
        stage('Search File') {
            when {
                expression {
                    env.SEARCH_TYPE == "File"
                }
            }
            steps {
                script {
                    search_file()
                }
            }
        }

        stage('Search Configuration') {
            when {
                expression {
                    env.SEARCH_TYPE == "Configuration"
                }
            }
            steps {
                script {
                    search_configuration()
                }
            }
        }

        stage('Generic Search') {
            when {
                expression {
                    env.SEARCH_TYPE == "Generic"
                }
            }
            steps {
                script {
                    generic_search()
                }
            }
        }
    }
    post {
        success {
            archiveArtifacts allowEmptyArchive: true, artifacts: "build/output.csv"
            archiveArtifacts allowEmptyArchive: true, artifacts: "build/output.html"
        }
    }
}

// Prepare
def prepare() {
    // Copy hybrid project lists from oss-common-ci-utils: dVersion-2.0.0-hybrid into the build/ directory in the Jenkins workspace.
    sh """
        rm -rf build || true
        mkdir -p build/project_lists
        [ -d oss-common-ci-utils ] && rm -rf oss-common-ci-utils
        git clone ${GERRIT_MIRROR}/OSS/com.ericsson.oss.ci/oss-common-ci-utils
        cd oss-common-ci-utils
        git checkout dVersion-2.0.0-hybrid
        cp dsl/projects_list_with_jobs_hybrid ../build/project_lists
        cp dsl/project_list_with_go_microservices ../build/project_lists
        cd ..
        [ -d oss-common-ci-utils ] && rm -rf oss-common-ci-utils
    """

    // Fetch the names of hybrid project lists in the build/ directory and save them to pr_list_names.txt
    sh """
        rm -f ${workspace}/pr_list_names.txt || true
        touch ${workspace}/pr_list_names.txt
        cd ${workspace}/build/project_lists && ls | tee ${workspace}/pr_list_names.txt
    """

    // Fetch project details from the hybrid project lists.
    def input_data = []
    def project_type = "LANG=${env.PROJECT_TYPE},"
    if ("${env.PROJECT_TYPE}" == "All Projects") {
        project_type = "LANG="
    }

    String[] project_lists = (new File("${workspace}/pr_list_names.txt").text).split('\n')
    for (String project_list in project_lists) {
        String[] project_data = (new File("${workspace}/build/project_lists/${project_list}").text).split('\n')
        for (data in project_data) {

            // Filter based on PROJECT_TYPE
            if (data.contains("${project_type}")) {

                // Gerrit Repo
                def gerrit_repo_name = ""
                def gerrit_repo_url = ""
                gerrit_repo_name = data.split(",")[0].replaceAll("\\s", "")
                gerrit_repo_url = "https://gerrit-gamma.gic.ericsson.se/#/admin/projects/${gerrit_repo_name}"

                // Jenkins Instance
                def jenkins_url = ""
                if (data.contains("fem1s11,")) {
                    jenkins_url = "https://fem1s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"
                } else if (data.contains("fem3s11,")) {
                    jenkins_url = "https://fem3s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"
                } else if (data.contains("fem6s11,")) {
                    jenkins_url = "https://fem6s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"
                }

                // Jenkins Job URL
                def pcr_url = ""
                def publish_url = ""
                def artifact_id = gerrit_repo_name.split('/').last()
                pcr_url = "${jenkins_url}${artifact_id}_PreCodeReview_Hybrid/"
                publish_url = "${jenkins_url}${artifact_id}_Publish_Hybrid/"

                // Microservice Language
                def lang = ""
                for (elem in data.split(",")) {
                    if (elem.contains("LANG=")) {
                        lang = elem.tokenize('=')[1]
                    }
                }

                // Data
                def data_string = "${lang},${gerrit_repo_name},${gerrit_repo_url},${pcr_url},${publish_url}"
                input_data.add(data_string)
            }
        }
    }
    return input_data
}

// Search File
def search_file() {

    // Input
    def input_data = prepare()

    // Output
    sh "touch ${workspace}/build/output.csv"
    sh "touch ${workspace}/build/output.html"
    def output_file = new File("${workspace}/build/output.csv")
    def output_report = new File("${workspace}/build/output.html")
    def output_header = "Project Type,Gerrit Repo,Gerrit URL,PCR Pipeline,Publish Pipeline,Search File Name,Results\n"
    output_file.append(output_header)

    // Compile
    for (data in input_data) {
        // Data
        def lang = data.split(",")[0]
        def repo_name = data.split(",")[1]
        def repo_url = data.split(",")[2]
        def pcr_url = data.split(",")[3]
        def publish_url = data.split(",")[4]
        def artifact_id = repo_name.split('/').last()
        def file_name = "${env.FILE_NAME}"
        def results = ""

        // Clone Gerrit Repo
        sh "git clone ${GERRIT_MIRROR}/${repo_name}"

        // Search
        try {
            if (file_name?.trim()) {
                results = sh(script: "find ${workspace}/${artifact_id} -name ${file_name} -type f", returnStdout: true)
                if (!(results?.trim())) {
                    results = "None"
                } else {
                    results = results.trim().replace("${workspace}/${artifact_id}/", "").replace("\n", " + ").replace(",", " ; ")
                }

                // Output
                def output_string = "${lang},${repo_name},${repo_url},${pcr_url},${publish_url},${file_name},${results}\n"
                output_file.append(output_string)
            }
        } catch (Exception e) {
            print(e)
        }

        // Cleanup
        sh "rm -rf ${workspace}/${artifact_id}"
    }

    // Report
    generate_html_report()
}


// Search Configuration
def search_configuration() {

    // Input
    def input_data = prepare()

    // Output
    sh "touch ${workspace}/build/output.csv"
    sh "touch ${workspace}/build/output.html"
    def output_file = new File("${workspace}/build/output.csv")
    def output_report = new File("${workspace}/build/output.html")
    def output_header = "Project Type,Gerrit Repo,Gerrit URL,PCR Pipeline,Publish Pipeline,File Name,File Exists,Search Text,Search Text Exists,Results\n"
    output_file.append(output_header)

    // Compile
    for (data in input_data) {
        // Data
        def lang = data.split(",")[0]
        def repo_name = data.split(",")[1]
        def repo_url = data.split(",")[2]
        def pcr_url = data.split(",")[3]
        def publish_url = data.split(",")[4]
        def artifact_id = repo_name.split('/').last()
        def file_name = "${env.FILE_NAME}"
        def file = "${workspace}/${artifact_id}/${file_name}"
        def key = "${env.SEARCH_TEXT}"
        def file_exists = ""
        def key_exists = ""
        def value = ""
        def results = ""

        // Clone Gerrit Repo
        sh "git clone ${GERRIT_MIRROR}/${repo_name}"

        // Search
        if (fileExists(file)) {
            file_exists = "Yes"
            String file_text = new File(file).text
            if (file_text.contains(key)) {
                key_exists = "Yes"
                for (String line in file_text.split("\n")) {
                    if (line.contains(key)) {
                        value = value + line.replace("\n", " + ").replace(",", " ; ")
                    }
                }
            } else {
                key_exists = "No"
                value = "None"
            }
        } else {
            file_exists = "No"
            key_exists = "No"
            value = "None"
        }

        // Output
        def output_string = "${lang},${repo_name},${repo_url},${pcr_url},${publish_url},${file_name},${file_exists},${key},${key_exists},${value}\n"
        output_file.append(output_string)

        // Cleanup
        sh "rm -rf ${workspace}/${artifact_id}"
    }

    // Report
    generate_html_report()
}


// Generic Search
def generic_search() {

    // Input
    def input_data = prepare()

    // Output
    sh "touch ${workspace}/build/output.csv"
    sh "touch ${workspace}/build/output.html"
    def output_file = new File("${workspace}/build/output.csv")
    def output_report = new File("${workspace}/build/output.html")
    def output_header = "Project Type,Gerrit Repo,Gerrit URL,PCR Pipelines,Publish Pipeline,Search Text,Results\n"
    output_file.append(output_header)

    // Compile
    for (data in input_data) {
        // Data
        def lang = data.split(",")[0]
        def repo_name = data.split(",")[1]
        def repo_url = data.split(",")[2]
        def pcr_url = data.split(",")[3]
        def publish_url = data.split(",")[4]
        def artifact_id = repo_name.split('/').last()
        def key = "${env.SEARCH_TEXT}"
        def results = ""

        // Clone Gerrit Repo
        sh "git clone ${GERRIT_MIRROR}/${repo_name}"

        // Search
        try {
            if (key?.trim()) {
                results = sh(script: "cd ${workspace}/${artifact_id} && grep -n ${key} -r --exclude-dir=bob --exclude=bob.py || true", returnStdout: true)
                if (!(results?.trim())) {
                    results = "None"
                } else {
                    results = results.trim().replace("${workspace}/${artifact_id}/", "").replace("\n", " + ").replace(",", " ; ")
                }

                // Output
                def output_string = "${lang},${repo_name},${repo_url},${pcr_url},${publish_url},${key},${results}\n"
                output_file.append(output_string)
            }
        } catch (Exception e) {
            print(e)
        }

        // Cleanup
        sh "rm -rf ${workspace}/${artifact_id}"
    }

    // Report
    generate_html_report()
}


// HTML Report Generation
def generate_html_report() {

    // Init
    def html_report = new File("${workspace}/build/output.html")
    def header = "<html>\n<head>\n<style> table, th, td { border: 1px solid rgb(255, 255, 255); border-collapse: collapse; font-size:14px;} th { background: #000; color: #eee; font-weight: bold; padding: 5px; text-align:left;} td { background: #aaa; font-weight: normal; overflow: hidden; padding: 5px; text-overflow: ellipsis; white-space: nowrap; } body { background: #e1e2e3; font-family: sans-serif; font-size:14px;}\n</style>\n</head>\n<body>\n<b>Hybrid Search Results</b>"
    def date = String.format('%tF %<tH:%<tM', java.time.LocalDateTime.now())
    html_report.append("${header}")
    html_report.append("\n<p><b>Report generated</b>: ${date}</p>\n")

    // Template
    def html_string = "<br><table>\n"
    def table_header = "<th>elem</th>"
    def table_data = "<td>elem</td>"
    def table_link = "<td><a href='elem'>Link</a></td>"
    def gerrit_url = "https://gerrit-gamma.gic.ericsson.se/#/admin/projects/"
    def jenkins_url = "eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"

    // Input
    String[] input_data = new File("${workspace}/build/output.csv").text.split('\n')
    int count = 1

    for (String data in input_data) {
        if (count == 1) {
            // Header
            html_string = html_string + "<tr>"
            for (String elem in data.split(",")) {
                temp = table_header.replace("elem", elem)
                html_string = html_string + temp
            }
            html_string = html_string + "</tr>\n"
        } else {
            // Data
            html_string = html_string + "<tr>"
            for (String elem in data.split(",")) {
                if (elem.contains(jenkins_url) || elem.contains(gerrit_url)) {
                    temp = table_link.replace("elem", elem)
                } else {
                    temp = table_data.replace("elem", elem.replace(" + ", "<br>"))
                }
                html_string = html_string + temp
            }
            html_string = html_string + "</tr>\n"
        }
        count = count + 1
    }
    html_string = html_string + "</table>\n<br><br>\n</body>\n</html>"
    html_report.append("${html_string}")
}