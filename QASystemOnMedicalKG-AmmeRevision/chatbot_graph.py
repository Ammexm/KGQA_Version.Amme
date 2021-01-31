# coding: utf-8
# File: AmmeRevision
# Update: 2021/1/31
# Blog:
# Origin Source:
# 1、https://github.com/liuhuanyong/QASystemOnMedicalKG
# 2、https://github.com/vivianLL/QASystemOnHepatopathyKG

from question_classifier import *
from question_parser import *
from answer_search import *


'''问答类'''
class ChatBotGraph:
    def __init__(self):
        # print("定义QuestionClassifier类型的成员变量classifier、QuestionPase类型的成员变量parser、AnswerSearcher类型的成员变量searcher")
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        # 问答框架包含问句分类、问句解析、查询结果三个步骤
        answer = '您好，我是肝病问答小助手，希望可以帮到您。祝您身体健康！'
        # 调用self.classifier.classify进行问句分类
        res_classify = self.classifier.classify(sent)
        # print(res_classify)
        if not res_classify:
            return '抱歉，小助手暂时无法回答您的问题，请咨询医生。'
        # 如果有分类结果，则调用self.parser.parser_main对问句进行解析
        res_sql = self.parser.parser_main(res_classify)
        # 再调用self.searcher.search_main查找对应的答案
        final_answers = self.searcher.search_main(res_sql)
        # 如果有则返回答案，如果没有则输出模板句式。
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)

if __name__ == '__main__':
    print("您好，欢迎进入医疗问答系统❗")
    handler = ChatBotGraph()
    while 1:
        # print("请输入问题")
        question = input("用户:");
        answer = handler.chat_main(question);
        print("小助手:"+answer)


