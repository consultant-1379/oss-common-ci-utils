import json
import subprocess
import sys

READY_TOPIC = 'HB_Review_Ready'
EARLY_FEEDBACK_TOPIC = 'HB_Early_Feedback'

review_ready_json_command='ssh -p 29418 gerrit-gamma.gic.ericsson.se gerrit query topic:' + READY_TOPIC + ' NOT status:merged NOT status:Abandoned  --comments --all-reviewers --patch-sets --format=JSON'
early_feedback_reviews_command='ssh -p 29418 gerrit-gamma.gic.ericsson.se gerrit query topic:' + EARLY_FEEDBACK_TOPIC + ' NOT status:merged NOT status:Abandoned  --comments --all-reviewers --patch-sets --format=JSON'

def get_number_of_reviewers(input):
    numberOfReviewers = 0
    if 'allReviewers' in input:
        # numberOfReviewers = len(input['allReviewers'])
        for reviewer in input['allReviewers']:
            if reviewer['username'] not in [input['owner']['username'], 'ossadmin', 'axisadm']:
                numberOfReviewers += 1
    return numberOfReviewers

def filter_reviews(input):
    output = []
    for entry in input:
        if 'owner' in entry:
            output.append(entry)
    return output

def filter_json(input):
    output = []
    for entry in input:
        if is_valid_jason(entry):
            output.append(json.loads(entry))
    return output

def is_valid_jason(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True

def get_reviews(json_command):
    return filter_reviews(filter_json(execute_command(json_command)))

def create_email_section(json_command):
    SECTION = '<table style ="width: 100%; border: solid #0082f0 1px;"><thead style="background-color: #0050ca; color: white;"><tr><th style="text-align: left;padding: 8px; width: 40%">Commit Message</th><th style="padding: 8px; width: 20%; text-align: center;">Link</th><th style="padding: 8px;  width: 20%; text-align: left;">Owner</th><th style="text-align: left;padding: 8px;  width: 20%;">Active Reviewers</th></tr></thead>'
    reviews =  get_reviews(json_command)
    for review in reviews:
        SECTION += '<tbody style="color: #244d4d; font-size: light; "><tr><td>' + review['subject'][:len(review['subject'])].split('\n')[0] + '</td> '
        SECTION += '<td  style="text-align: center; "><a href=\"' + review['url'] + '\">' + review['url'] + '</a></td>'
        SECTION += '<td  style="text-align: right; ">' + review['owner']['name'] + ' </td>'
        SECTION += '<td  style="text-align: right; ">' + str(get_number_of_reviewers(review)) + '</td></tr>'
    SECTION += '</tbody></table></br>'
    return SECTION

def execute_command(command):
    p = subprocess.Popen([command], stdout=subprocess.PIPE, stderr=None, shell=True)
    bytes = p.communicate()[0]
    text = bytes.decode('utf-8')
    lines = text.split('\n')
    return lines

def fetchGerriReview():
    EMAIL_CONTENT = '<p>Hello Team :-)</b><br></p>'
    EMAIL_CONTENT += '<p>Below is a list of open code reviews categorized by different topics. <b>Note</b>: Only the open code reviews are shown here, the abandoned reviews are excluded.</p>'
    EMAIL_CONTENT += '<p>For more information on the topics, please refer to <a href="https://eteamspace.internal.ericsson.com/x/zCBke">confluence</a></p>'
    EMAIL_CONTENT += "<b style='color: #244d4d; font-size:16px; margin-bottom:-10px;'>HB_Review_Ready:</b><br><br>"
    EMAIL_CONTENT += create_email_section(review_ready_json_command)
    EMAIL_CONTENT += "<b style='color: #244d4d; font-size:16px; margin-bottom:-10px;'>HB_Early_Feedback:</b><br><br>"
    EMAIL_CONTENT += create_email_section(early_feedback_reviews_command)

    # write email.properties files
    file = open( 'email.properties', 'w' )
    file.write( EMAIL_CONTENT.encode("utf-8") + '\n' )
    file.close()

if __name__ == "__main__":
    reviews = get_reviews(review_ready_json_command) + get_reviews(early_feedback_reviews_command);
    if len(reviews) == 0:
        sys.exit(0)
    else:
        fetchGerriReview()