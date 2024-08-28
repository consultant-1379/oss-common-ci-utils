import os
import subprocess
import fnmatch

# Clone the 'OSS/com.ericsson.oss.ci/oss-common-ci-utils' repository and checkout 'dVersion-2.0.0-hybrid' branch
common_ci_utils_repo_url = "https://gerrit-gamma.gic.ericsson.se/OSS/com.ericsson.oss.ci/oss-common-ci-utils.git"
common_ci_utils_branch = "dVersion-2.0.0-hybrid"
common_ci_utils_dir = "oss-common-ci-utils"

subprocess.call(["git", "clone", "-b", common_ci_utils_branch, common_ci_utils_repo_url, common_ci_utils_dir])

# Read the list of projects from the 'projects_list_with_jobs_hybrid' file and extract only repository names
projects_file = os.path.join(common_ci_utils_dir, 'dsl', 'projects_list_with_jobs_hybrid')
with open(projects_file, 'r') as file:
    projects = [line.strip().split(',')[0] for line in file.readlines()]

keycloak_repos = []

for project in projects:
    # Clone the repository
    repo_name = project.split("/")[-1]
    subprocess.call(["git", "clone", "https://gerrit-gamma.gic.ericsson.se/{}.git".format(project)])


    # Recursive directory search for eric-product-info.yaml
    for root, _, files in os.walk(repo_name):
        for file in fnmatch.filter(files, "eric-product-info.yaml"):
            yaml_path = os.path.join(root, file)
            with open(yaml_path, "r") as yaml_file:
                yaml_content = yaml_file.read()
                # Check if "keycloakClient" is in the YAML content
                if "keycloakClient" in yaml_content:
                    keycloak_repos.append(project)
                    break  # No need to check further in this repository

# Print repositories with keycloakClient variable
print("Repositories with keycloakClient:")
for repo in keycloak_repos:
    print(repo)
