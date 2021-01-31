# coding: utf-8
# File: AmmeRevision
# Update: 2021/1/31
# Blog:
# Origin Source:
# 1、https://github.com/liuhuanyong/QASystemOnMedicalKG
# 2、https://github.com/vivianLL/QASystemOnHepatopathyKG

# 解决报错：python的str默认是ascii编码，和unicode编码冲突

# version: python3
import importlib,sys
importlib.reload(sys)

# version: python2
# import sys
# reload(sys)
# sys.setdefaultencoding(‘utf-8’)

import os
import json
from py2neo import Graph,Node
import io

class MedicalGraph:
    def __init__(self):
        print("start init");
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/medical.json')
        # self.g=Graph("bolt://localhost:7687", username="neo4j", password="test");
        self.g = Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            http_port=7474,  # neo4j 服务器监听的端口号
            password="test",
            user="neo4j", )
        # 数据库user name，如果没有更改过，应该是neo4j


    '''读取文件'''
    def read_nodes(self):
        print("read_nodes");
        # 共７类节点
        drugs = [] # 药品
        foods = [] #　食物
        checks = [] # 检查
        departments = [] #科室
        producers = [] #药品大类
        diseases = [] #疾病
        symptoms = []#症状

        disease_infos = []#疾病信息

        # 构建节点实体关系
        rels_department = [] #　科室－科室关系
        rels_noteat = [] # 疾病－忌吃食物关系
        rels_doeat = [] # 疾病－宜吃食物关系
        rels_recommandeat = [] # 疾病－推荐吃食物关系
        rels_commonddrug = [] # 疾病－通用药品关系
        rels_recommanddrug = [] # 疾病－热门药品关系
        rels_check = [] # 疾病－检查关系
        rels_drug_producer = [] # 厂商－药物关系

        rels_symptom = [] #疾病症状关系
        rels_acompany = [] # 疾病并发关系
        rels_category = [] #　疾病与科室之间的关系

        count = 0
        for data in io.open(self.data_path,encoding="utf-8"):
            disease_dict = {}
            count += 1
            data_json = json.loads(data)
            disease = data_json['name']
            disease_dict['name'] = disease
            diseases.append(disease)
            disease_dict['desc'] = ''
            disease_dict['prevent'] = ''
            disease_dict['cause'] = ''
            disease_dict['easy_get'] = ''
            disease_dict['cure_department'] = ''
            disease_dict['cure_way'] = ''
            disease_dict['cure_lasttime'] = ''
            disease_dict['symptom'] = ''
            disease_dict['cured_prob'] = ''

            # 构建疾病和症状的关系
            if 'symptom' in data_json:
                symptoms += data_json['symptom']
                for symptom in data_json['symptom']:
                    rels_symptom.append([disease, symptom])

            # 构建疾病和并发症关系
            if 'acompany' in data_json:
                for acompany in data_json['acompany']:
                    rels_acompany.append([disease, acompany])

            # 存储疾病描述
            if 'desc' in data_json:
                disease_dict['desc'] = data_json['desc']

            # 存储疾病预防
            if 'prevent' in data_json:
                disease_dict['prevent'] = data_json['prevent']

            # 存储疾病成因
            if 'cause' in data_json:
                disease_dict['cause'] = data_json['cause']

            # 存储患病比例
            if 'get_prob' in data_json:
                disease_dict['get_prob'] = data_json['get_prob']

            # 存储易感人群
            if 'easy_get' in data_json:
                disease_dict['easy_get'] = data_json['easy_get']

            # 存储就诊科室
            if 'cure_department' in data_json:
                cure_department = data_json['cure_department']
                # 只有一个就诊科室
                if len(cure_department) == 1:
                     rels_category.append([disease, cure_department[0]])
                # 有两个就诊科室
                if len(cure_department) == 2:
                    big = cure_department[0]
                    small = cure_department[1]
                    # 构建科室间的关系
                    rels_department.append([small, big])
                    # 构建疾病与科室之间的关系
                    rels_category.append([disease, small])

                disease_dict['cure_department'] = cure_department
                departments += cure_department

            # 存储治疗方式
            if 'cure_way' in data_json:
                disease_dict['cure_way'] = data_json['cure_way']

            # 存储治疗周期
            if  'cure_lasttime' in data_json:
                disease_dict['cure_lasttime'] = data_json['cure_lasttime']

            # 存储治愈率
            if 'cured_prob' in data_json:
                disease_dict['cured_prob'] = data_json['cured_prob']

            # 存储常用药物
            if 'common_drug' in data_json:
                common_drug = data_json['common_drug']
                for drug in common_drug:
                    rels_commonddrug.append([disease, drug])
                drugs += common_drug


            if 'recommand_drug' in data_json:
                recommand_drug = data_json['recommand_drug']
                # 加入药品类
                drugs += recommand_drug
                # 构建疾病和常用药物之间的关系
                for drug in recommand_drug:
                    rels_recommanddrug.append([disease, drug])

            # 存储忌食食物
            if 'not_eat' in data_json:
                not_eat = data_json['not_eat']
                # 构建忌食食物和疾病间的关系
                for _not in not_eat:
                    rels_noteat.append([disease, _not])
                # 食物中加入忌食食物
                foods += not_eat

                # 存储宜食食物
                do_eat = data_json['do_eat']
                # 构建宜食食物和疾病的关系
                for _do in do_eat:
                    rels_doeat.append([disease, _do])
                # 食物中加入宜食食物
                foods += do_eat

                # 存储推荐食物
                recommand_eat = data_json['recommand_eat']
                # 构建推荐食物和疾病间的关系
                for _recommand in recommand_eat:
                    rels_recommandeat.append([disease, _recommand])
                # 食物中加入推荐食物
                foods += recommand_eat

            # 存储检查结果
            if 'check' in data_json:
                check = data_json['check']
                # 构建疾病和检查的关系
                for _check in check:
                    rels_check.append([disease, _check])
                checks += check

            # 存储药品明细
            if 'drug_detail' in data_json:
                drug_detail = data_json['drug_detail']
                producer = [i.split('(')[0] for i in drug_detail]
                # 构建厂商-药物之间的关系
                rels_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail]
                # 加入厂商名称
                producers += producer
            # 存入疾病信息
            disease_infos.append(disease_dict)
        # print(drugs);
        return set(drugs), set(foods), set(checks), set(departments), set(producers), set(symptoms), set(diseases), disease_infos,\
               rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,\
               rels_symptom, rels_acompany, rels_category

    '''创建图节点'''
    # 3 create node_info
    def create_node(self, label, nodes):
        print("create_node");
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            # print(count, len(nodes))
        return

    # 知识图谱中主要包含两类节点
    # 一类为中心疾病节点，包含各种疾病属性；
    # 一类为普通实体节点，即药品、食物等，不包含属性

    '''创建知识图谱中心疾病的节点'''
    # 2 create a node
    def create_diseases_nodes(self, disease_infos):
        print("create_diseases_nodes");
        count = 0;
        for disease_dict in disease_infos:
            node = Node("Disease", name=disease_dict['name'], desc=disease_dict['desc'],
                        prevent=disease_dict['prevent'] ,cause=disease_dict['cause'],
                        easy_get=disease_dict['easy_get'],cure_lasttime=disease_dict['cure_lasttime'],
                        cure_department=disease_dict['cure_department']
                        ,cure_way=disease_dict['cure_way'] , cured_prob=disease_dict['cured_prob'])
            self.g.create(node)
            count += 1
            print(count)
        print(count);
        return

    '''创建知识图谱实体节点类型schema'''
    # 1 creat type of nodes
    def create_graphnodes(self):
        print("create_graphnodes");
        # 获取数据
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos,rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        # 创建疾病节点
        self.create_diseases_nodes(disease_infos)
        # 创建药品节点
        self.create_node('Drug', Drugs)
        # print('length of Drug: '+len(Drugs))
        # 创建食物节点
        self.create_node('Food', Foods)
        # print('length of Food: '+len(Foods))
        # 创建检查节点
        self.create_node('Check', Checks)
        # print('length of Check: '+len(Checks))
        # 创建科室节点
        self.create_node('Department', Departments)
        # print('length of Department: '+len(Departments))
        # 输出厂商节点
        self.create_node('Producer', Producers)
        # print('length of Producer: '+len(Producers))
        # 创建症状节点
        self.create_node('Symptom', Symptoms)
        return


    '''创建实体关系边'''
    # 4 creat edges
    def create_graphrels(self):
        print("create_graphrels");
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_relationship('Disease', 'Food', rels_recommandeat, 'recommand_eat', '推荐食谱')
        self.create_relationship('Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
        self.create_relationship('Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
        self.create_relationship('Department', 'Department', rels_department, 'belongs_to', '属于')
        self.create_relationship('Disease', 'Drug', rels_commonddrug, 'common_drug', '常用药品')
        self.create_relationship('Producer', 'Drug', rels_drug_producer, 'drugs_of', '生产药品')
        self.create_relationship('Disease', 'Drug', rels_recommanddrug, 'recommand_drug', '好评药品')
        self.create_relationship('Disease', 'Check', rels_check, 'need_check', '诊断检查')
        self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状')
        self.create_relationship('Disease', 'Disease', rels_acompany, 'acompany_with', '并发症')
        self.create_relationship('Disease', 'Department', rels_category, 'belongs_to', '所属科室')

    '''创建实体关联边'''
    # 5 creat relationship of edges
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        print("create_relationship");
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

    '''导出数据'''
    def export_data(self):
        print("export_data");
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category = self.read_nodes()
        f_drug = open('export/drug.txt', 'w+')
        f_food = open('export/food.txt', 'w+')
        f_check = open('export/check.txt', 'w+')
        f_department = open('export/department.txt', 'w+')
        f_producer = open('export/producer.txt', 'w+')
        f_symptom = open('export/symptoms.txt', 'w+')
        f_disease = open('export/disease.txt', 'w+')

        f_drug.write('\n'.join(list(Drugs)))
        f_food.write('\n'.join(list(Foods)))
        f_check.write('\n'.join(list(Checks)))
        f_department.write('\n'.join(list(Departments)))
        f_producer.write('\n'.join(list(Producers)))
        f_symptom.write('\n'.join(list(Symptoms)))
        f_disease.write('\n'.join(list(Diseases)))

        f_drug.close()
        f_food.close()
        f_check.close()
        f_department.close()
        f_producer.close()
        f_symptom.close()
        f_disease.close()

        return

if __name__ == '__main__':

    handler = MedicalGraph()

    handler.create_graphnodes();
    handler.create_graphrels();

    # handler.export_data()
    # 知识库包含7类规模为4.4万的知识实体，11类规模约30万实体关系

    print("Graph Create Successfully")