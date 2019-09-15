import json
import requests

# url = 'https://leetcode-cn.com/api/problems/all/'
# r = requests.get(url,verify=False)

# print(r.text)

# d = json.load(open('problem.json'))
# for dd in d['stat_status_pairs']:
# 	print(dd['stat']['question__title_slug'])

# print(type(d))
file='problem.json'
PROBLEMS = json.load(open(file))

def problems():
	for dd in PROBLEMS['stat_status_pairs']:
		yield dd['stat']['question__title_slug']
		

headers = """
Host: leetcode-cn.com
Content-Type: application/json
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Referer: https://leetcode-cn.com/problemset/all/
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: __atuvc=46%7C33%2C0%7C34%2C0%7C35%2C0%7C36%2C1%7C37; csrftoken=GsrXST7vhlHKrZVdxrPV00bpj3Kzm3e4WB5Z2yYSvxNNkWeCYnlf4eX7njC3mr27
"""
headers = dict(x.split(': ',1) for x in headers.splitlines() if x)


def get_problem_by_name(name):
	
	data = {"operationName":"questionData","variables":{"titleSlug":name},"query":"query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    enableTestMode\n    envInfo\n    __typename\n  }\n}\n"}

	r = requests.post('https://leetcode-cn.com/graphql',data=json.dumps(data),verify=False,headers=headers)

	a = json.loads(r.text)
	q = a['data']['question']		

	p = dict()
	p['titleslug'] = q['titleSlug']
	p['content'] =	q['translatedContent'] 
	p['title'] = q['translatedTitle']
	p['testcase'] = q['sampleTestCase']
	try:
		p['code'] = q['codeSnippets'][2]['code']
	except:
		p['code'] = ''
	p['tags'] = [x['translatedName'] for x in q['topicTags']]

	return q,p


def main():
	i = 0
	for p in problems():
		i += 1
		p = get_problem_by_name(p)
		with open('p.json','a') as f:
			json.dump(p,f)
		print(i, p['title'])

if __name__ == '__main__':
	q,p = get_problem_by_name('two-sum')
	print(q)