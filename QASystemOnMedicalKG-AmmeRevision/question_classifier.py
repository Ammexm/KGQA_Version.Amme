# coding: utf-8
# File: AmmeRevision
# Update: 2021/1/31
# Blog:
# Origin Source:
# 1、https://github.com/liuhuanyong/QASystemOnMedicalKG
# 2、https://github.com/vivianLL/QASystemOnHepatopathyKG

# 定义意图识别分类器类
import os
import ahocorasick
import io

class QuestionClassifier:
    # 加载知识图谱中的8类实体数据，并且根据实体数据构建ac自动机，定义问题分类的特征词
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        # 特征词路径
        self.disease_path = os.path.join(cur_dir, 'dict/disease.txt')
        self.department_path = os.path.join(cur_dir, 'dict/department.txt')
        self.check_path = os.path.join(cur_dir, 'dict/check.txt')
        self.drug_path = os.path.join(cur_dir, 'dict/drug.txt')
        self.food_path = os.path.join(cur_dir, 'dict/food.txt')
        self.producer_path = os.path.join(cur_dir, 'dict/producer.txt')
        self.symptom_path = os.path.join(cur_dir, 'dict/symptom.txt')
        self.deny_path = os.path.join(cur_dir, 'dict/deny.txt')
        # 加载特征词
        self.disease_wds= [i.strip() for i in io.open(self.disease_path,encoding='utf-8') if i.strip()]
        self.department_wds= [i.strip() for i in io.open(self.department_path, encoding='UTF-8') if i.strip()]
        self.check_wds= [i.strip() for i in io.open(self.check_path, encoding='UTF-8') if i.strip()]
        self.drug_wds= [i.strip() for i in io.open(self.drug_path, encoding='UTF-8') if i.strip()]
        self.food_wds= [i.strip() for i in io.open(self.food_path, encoding='UTF-8') if i.strip()]
        self.producer_wds= [i.strip() for i in io.open(self.producer_path, encoding='UTF-8') if i.strip()]
        self.symptom_wds= [i.strip() for i in io.open(self.symptom_path, encoding='UTF-8') if i.strip()]
        self.region_words = set(self.department_wds + self.disease_wds + self.check_wds + self.drug_wds + self.food_wds + self.producer_wds + self.symptom_wds)
        self.deny_words = [i.strip() for i in io.open(self.deny_path, encoding='UTF-8') if i.strip()]
        # 构造领域 actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()

        # 补充个别问句疑问词
        self.symptom_qwds = ['症状', '表征', '现象', '症候', '表现', '会引起']
        self.cause_qwds = ['原因', '成因', '病因', '为什么', '怎么会', '怎样才', '咋样才', '怎样会', '如何会', '为啥', '为何', '如何才会', '怎么才会',
                           '会导致', '会造成']
        self.acompany_qwds = ['并发症', '并发', '一起发生', '一并发生', '一起出现', '一并出现', '一同发生', '一同出现', '伴随发生', '伴随', '共现', '引起',
                              '有关']
        self.food_qwds = ['饮食', '饮用', '吃', '食', '伙食', '膳食', '喝', '菜', '忌口', '补品', '保健品', '食谱', '菜谱', '食用', '食物', '补品']
        self.drug_qwds = ['吃', '药', '药品', '用药', '胶囊', '口服液', '炎片']
        self.prevent_qwds = ['预防', '防范', '抵制', '抵御', '防止', '躲避', '逃避', '避开', '免得', '逃开', '避开', '避掉', '躲开', '躲掉', '绕开',
                             '怎样才能不', '怎么才能不', '咋样才能不', '咋才能不', '如何才能不',
                             '怎样才不', '怎么才不', '咋样才不', '咋才不', '如何才不',
                             '怎样才可以不', '怎么才可以不', '咋样才可以不', '咋才可以不', '如何可以不',
                             '怎样才可不', '怎么才可不', '咋样才可不', '咋才可不', '如何可不', '日常', '护理']
        self.lasttime_qwds = ['周期', '多久', '多长时间', '多少时间', '几天', '几年', '多少天', '多少小时', '几个小时', '多少年']
        self.cureway_qwds = ['怎么治疗', '如何医治', '怎么医治', '怎么治', '怎么医', '如何治', '医治方式', '疗法', '咋治', '怎么办', '咋办', '咋治']
        self.cureprob_qwds = ['多大概率能治好', '多大几率能治好', '治好希望大么', '几率', '几成', '比例', '可能性', '能治', '可治', '可以治', '可以医']
        self.getway_qwds = ['传染']
        self.easyget_qwds = ['易感人群', '容易感染', '易发人群', '什么人', '哪些人', '感染', '染上', '得上']
        self.check_qwds = ['检查', '检查项目', '查出', '检查', '测出', '试出']
        self.belong_qwds = ['属于什么科', '属于', '什么科', '科室']
        self.cure_qwds = ['治疗什么', '治啥', '治疗啥', '医治啥', '治愈啥', '主治啥', '主治什么', '有什么用', '有何用', '用处', '用途',
                          '有什么好处', '有什么益处', '有何益处', '用来', '用来做啥', '用来作甚', '需要', '要', '可以治']

        # print("classify model init finished ......")
        return

    '''1th: 过滤问句'''
    '''2th: 此处是医疗实体识别，算法需要修改，按申报书的方法，需要使用：基于字－词网格LSTM－CRF模型（bi-lstm-crf）'''
    def check_medical(self, question):
        # 通过ahocorasick库的iter()函数匹配领域词，将有重复字符串的领域词去除短的，取最长的领域词返回。
        # 功能为过滤问句中含有的领域词，返回{问句中的领域词：词所对应的实体类型}。
        region_wds = []
        for i in self.region_tree.iter(question):   # ahocorasick库 匹配问题  iter返回一个元组，i的形式如(3, (23192, '乙肝'))
            wd = i[1][1]      # 匹配到的词
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)       # stop_wds取重复的短的词，如region_wds=['乙肝', '肝硬化', '硬化']，则stop_wds=['硬化']
        final_wds = [i for i in region_wds if i not in stop_wds]     # final_wds取长词
        final_dict = {i:self.wdtype_dict.get(i) for i in final_wds}  # 获取词和词所对应的实体类型
        global diseases_dict
        if final_dict:
            diseases_dict = final_dict
        # print("final_dict : ",final_dict)
        # if 'diseases_dict' in globals():
        #     print("diseases_dict : ",diseases_dict)
        # else:
        #     print("diseases_dict does not exist.")
        return final_dict

    '''根据特征词进行句子分类'''
    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False

    '''构造词对应的类型'''
    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.disease_wds:
                wd_dict[wd].append('disease')
            if wd in self.department_wds:
                wd_dict[wd].append('department')
            if wd in self.check_wds:
                wd_dict[wd].append('check')
            if wd in self.drug_wds:
                wd_dict[wd].append('drug')
            if wd in self.food_wds:
                wd_dict[wd].append('food')
            if wd in self.symptom_wds:
                wd_dict[wd].append('symptom')
            if wd in self.producer_wds:
                wd_dict[wd].append('producer')
        return wd_dict

    '''构造actree，加速过滤'''
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            word = str(word)
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''分类主函数'''
    def classify(self, question):
        data = {}
        medical_dict = self.check_medical(question)
        if not medical_dict:
            if 'diseases_dict' in globals():    # 判断是否是首次提问，若首次提问，则diseases_dict无值
                medical_dict = diseases_dict
            else:
                return {}
        # print("medical_dict : ", medical_dict)
        data['args'] = medical_dict
        #收集问句当中所涉及到的实体类型
        types = []
        for type_ in medical_dict.values():
            types += type_
        question_type = 'others'

        question_types = []

        # 症状
        if self.check_words(self.symptom_qwds, question) and ('disease' in types):
            question_type = 'disease_symptom'
            question_types.append(question_type)

        if self.check_words(self.symptom_qwds, question) and ('symptom' in types):
            question_type = 'symptom_disease'
            question_types.append(question_type)

        # 原因
        if self.check_words(self.cause_qwds, question) and ('disease' in types):
            question_type = 'disease_cause'
            question_types.append(question_type)
        # 并发症
        if self.check_words(self.acompany_qwds, question) and ('disease' in types):
            question_type = 'disease_acompany'
            question_types.append(question_type)

        # 推荐食品
        if self.check_words(self.food_qwds, question) and 'disease' in types:
            deny_status = self.check_words(self.deny_words, question)
            if deny_status:
                question_type = 'disease_not_food'
            else:
                question_type = 'disease_do_food'
            if self.check_words(['能吃', '能喝', '可以吃', '可以喝'], question): #增加了一个疾病属性：can_eat，对应增加了一个问题分类：
                question_types.append('disease_can_eat')
            # print(question_type)
            question_types.append(question_type)

        #已知食物找疾病
        if self.check_words(self.food_qwds+self.cure_qwds, question) and 'food' in types:
            deny_status = self.check_words(self.deny_words, question)
            if deny_status:
                question_type = 'food_not_disease'
            else:
                question_type = 'food_do_disease'
            question_types.append(question_type)

        # 推荐药品
        if self.check_words(self.drug_qwds, question) and 'disease' in types:
            question_type = 'disease_drug'
            question_types.append(question_type)

        # 药品治啥病
        if self.check_words(self.cure_qwds, question) and 'drug' in types:
            question_type = 'drug_disease'
            question_types.append(question_type)

        # 疾病接受检查项目
        if self.check_words(self.check_qwds, question) and 'disease' in types:
            question_type = 'disease_check'
            question_types.append(question_type)

        # 已知检查项目查相应疾病
        if self.check_words(self.check_qwds+self.cure_qwds, question) and 'check' in types:
            question_type = 'check_disease'
            question_types.append(question_type)

        #　症状防御
        if self.check_words(self.prevent_qwds, question) and 'disease' in types:
            question_type = 'disease_prevent'
            question_types.append(question_type)

        # 疾病医疗周期
        if self.check_words(self.lasttime_qwds, question) and 'disease' in types:
            question_type = 'disease_lasttime'
            question_types.append(question_type)

        # 疾病治疗方式
        if self.check_words(self.cureway_qwds, question) and 'disease' in types:
            question_type = 'disease_cureway'
            question_types.append(question_type)

        # 疾病治愈可能性
        if self.check_words(self.cureprob_qwds, question) and 'disease' in types:
            question_type = 'disease_cureprob'
            question_types.append(question_type)

        # 疾病易感染人群
        if self.check_words(self.easyget_qwds, question) and 'disease' in types :
            question_type = 'disease_easyget'
            question_types.append(question_type)

        # 若没有查到相关的外部查询信息，那么则将该疾病的描述信息返回
        if question_types == [] and 'disease' in types:
            question_types = ['disease_desc']

        # 若没有查到相关的外部查询信息，那么则将该症状的描述信息返回
        if question_types == [] and 'symptom' in types:
            question_types = ['symptom_disease']

        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types

        return data

if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        data = handler.classify(question)
        #print(data);