from typing import List, Dict, Optional
from models import Question, QuestionCategory
import uuid
import re


class QuestionGenerator:
    def __init__(self):
        self.question_counter = 0
        self._init_question_templates()
        self._init_entity_patterns()
    
    def _init_entity_patterns(self):
        self.person_titles = [
            "总", "经理", "总监", "老板", "老师", "教授", "医生", "护士",
            "工程师", "设计师", "会计", "律师", "警察", "消防员", "司机",
            "同学", "同事", "朋友", "家人", "亲戚", "领导", "下属", "员工"
        ]
        
        self.person_prefixes = ["老", "小", "大"]
        self.conjunctions = ["和", "与", "及", "跟", "、", "，", ",", "；", ";", "还有"]
    
    def _init_question_templates(self):
        self.level1_templates = {
            QuestionCategory.PERSON: [
                "谁参与了这个事件？",
                "这个事件的主体是谁？",
                "涉及哪些人物？"
            ],
            QuestionCategory.OBJECT: [
                "这个事件涉及什么事物？",
                "使用了什么物品或工具？",
                "有哪些相关的对象？"
            ],
            QuestionCategory.EVENT: [
                "这个事件发生在什么时候？",
                "这个事件发生在哪里？",
                "这个事件的具体内容是什么？"
            ]
        }
        
        self.person_detail_questions = [
            "{entity}是谁？",
            "{entity}的身份是什么？",
            "{entity}有什么特点？",
            "{entity}来自哪里？",
            "{entity}多大年纪？",
            "{entity}的职位是什么？",
            "{entity}负责什么工作？"
        ]
        
        self.object_detail_questions = [
            "{entity}具体是什么？",
            "{entity}有什么特点？",
            "{entity}来自哪里？",
            "{entity}的用途是什么？",
            "{entity}的数量有多少？",
            "{entity}的价格是多少？",
            "{entity}是谁提供的？"
        ]
        
        self.event_detail_questions = [
            "{entity}的具体时间是？",
            "{entity}的具体地点是？",
            "{entity}持续了多久？",
            "{entity}是如何发生的？",
            "{entity}的结果是什么？",
            "{entity}有什么影响？"
        ]
        
        self.smart_keywords = {
            "上课": {
                QuestionCategory.PERSON: ["谁上课了？", "和谁一起上课？", "老师是谁？"],
                QuestionCategory.OBJECT: ["上的什么课程？", "使用什么教材？", "在哪个教室上课？"],
                QuestionCategory.EVENT: ["什么时候上课？", "上课持续了多久？", "今天学习的内容是什么？"]
            },
            "吃饭": {
                QuestionCategory.PERSON: ["谁吃饭了？", "和谁一起吃的？", "谁做的饭？"],
                QuestionCategory.OBJECT: ["吃的什么？", "在哪里吃的？", "花费了多少钱？"],
                QuestionCategory.EVENT: ["什么时候吃的？", "吃了多久？", "饭菜味道如何？"]
            },
            "工作": {
                QuestionCategory.PERSON: ["谁在工作？", "和谁一起工作？", "领导是谁？"],
                QuestionCategory.OBJECT: ["做的什么工作？", "使用什么工具？", "工作地点在哪里？"],
                QuestionCategory.EVENT: ["什么时候工作？", "工作了多久？", "工作完成情况如何？"]
            },
            "学习": {
                QuestionCategory.PERSON: ["谁在学习？", "和谁一起学习？", "老师是谁？"],
                QuestionCategory.OBJECT: ["学习什么内容？", "使用什么教材？", "在哪里学习？"],
                QuestionCategory.EVENT: ["什么时候学习？", "学习了多久？", "学习效果如何？"]
            },
            "旅游": {
                QuestionCategory.PERSON: ["谁去旅游了？", "和谁一起去的？", "导游是谁？"],
                QuestionCategory.OBJECT: ["去了哪里旅游？", "乘坐什么交通工具？", "花费了多少钱？"],
                QuestionCategory.EVENT: ["什么时候去的？", "旅游了几天？", "旅游感受如何？"]
            },
            "购物": {
                QuestionCategory.PERSON: ["谁在购物？", "和谁一起购物？", "售货员是谁？"],
                QuestionCategory.OBJECT: ["买了什么东西？", "在哪里买的？", "花费了多少钱？"],
                QuestionCategory.EVENT: ["什么时候买的？", "购物花了多久？", "对购买的商品满意吗？"]
            },
            "开会": {
                QuestionCategory.PERSON: ["谁参加了会议？", "会议主持人是谁？", "有多少人参加？"],
                QuestionCategory.OBJECT: ["会议主题是什么？", "在哪里开会？", "使用什么设备？"],
                QuestionCategory.EVENT: ["什么时候开会？", "会议持续了多久？", "会议结果是什么？"]
            },
            "运动": {
                QuestionCategory.PERSON: ["谁在运动？", "和谁一起运动？", "教练是谁？"],
                QuestionCategory.OBJECT: ["做的什么运动？", "在哪里运动？", "使用什么器材？"],
                QuestionCategory.EVENT: ["什么时候运动？", "运动了多久？", "运动感受如何？"]
            }
        }
    
    def _extract_person_entities(self, text: str) -> List[str]:
        entities = []
        
        for conj in self.conjunctions:
            text = text.replace(conj, "|")
        
        parts = re.split(r'[|、，,；;\s]+', text)
        parts = [p.strip() for p in parts if p.strip()]
        
        for part in parts:
            if len(part) >= 1:
                for title in self.person_titles:
                    if title in part and len(part) > len(title):
                        entities.append(part)
                        break
                else:
                    if len(part) >= 2 or (len(part) == 1 and part[0] in self.person_prefixes):
                        entities.append(part)
        
        entities = [e for e in entities if len(e) >= 1]
        
        return entities if entities else [text.strip()]
    
    def _extract_object_entities(self, text: str) -> List[str]:
        entities = []
        
        for conj in self.conjunctions:
            text = text.replace(conj, "|")
        
        parts = re.split(r'[|、，,；;\s]+', text)
        parts = [p.strip() for p in parts if p.strip()]
        
        for part in parts:
            if len(part) >= 1:
                entities.append(part)
        
        return entities if entities else [text.strip()]
    
    def _generate_question_id(self) -> str:
        self.question_counter += 1
        return f"q_{self.question_counter}_{uuid.uuid4().hex[:8]}"
    
    def generate_level1_questions(self, event_text: str) -> List[Question]:
        questions = []
        
        matched_keyword = None
        for keyword, templates in self.smart_keywords.items():
            if keyword in event_text:
                matched_keyword = keyword
                break
        
        if matched_keyword:
            templates = self.smart_keywords[matched_keyword]
            for category in [QuestionCategory.PERSON, QuestionCategory.OBJECT, QuestionCategory.EVENT]:
                if category in templates:
                    for q_text in templates[category][:3]:
                        question = Question(
                            id=self._generate_question_id(),
                            text=q_text,
                            category=category,
                            level=1
                        )
                        questions.append(question)
        else:
            for category in [QuestionCategory.PERSON, QuestionCategory.OBJECT, QuestionCategory.EVENT]:
                templates = self.level1_templates[category]
                for q_text in templates[:3]:
                    question = Question(
                        id=self._generate_question_id(),
                        text=q_text,
                        category=category,
                        level=1
                    )
                    questions.append(question)
        
        return questions
    
    def generate_level2_questions(self, parent_answer_id: str, answer_text: str, parent_category: QuestionCategory) -> List[Question]:
        questions = []
        
        if not answer_text or not answer_text.strip():
            return questions
        
        if parent_category == QuestionCategory.PERSON:
            entities = self._extract_person_entities(answer_text)
            templates = self.person_detail_questions
        elif parent_category == QuestionCategory.OBJECT:
            entities = self._extract_object_entities(answer_text)
            templates = self.object_detail_questions
        else:
            entities = [answer_text.strip()]
            templates = self.event_detail_questions
        
        for entity in entities:
            if not entity or not entity.strip():
                continue
            
            entity = entity.strip()
            
            questions_for_entity = []
            for template in templates:
                q_text = template.replace("{entity}", entity)
                questions_for_entity.append(q_text)
            
            selected_questions = questions_for_entity[:3]
            
            for i, q_text in enumerate(selected_questions):
                if i == 0:
                    category = QuestionCategory.PERSON
                elif i == 1:
                    category = QuestionCategory.OBJECT
                else:
                    category = QuestionCategory.EVENT
                
                question = Question(
                    id=self._generate_question_id(),
                    text=q_text,
                    category=category,
                    level=2,
                    parent_answer_id=parent_answer_id
                )
                questions.append(question)
        
        return questions
    
    def generate_level3_questions(self, parent_answer_id: str, answer_text: str, parent_category: QuestionCategory) -> List[Question]:
        questions = []
        
        if not answer_text or not answer_text.strip():
            return questions
        
        answer_text = answer_text.strip()
        
        followup_templates = {
            QuestionCategory.PERSON: [
                f"关于'{answer_text}'，还有什么需要补充的信息？",
                f"'{answer_text}'的详细背景是什么？",
                f"'{answer_text}'与这个事件有什么关系？"
            ],
            QuestionCategory.OBJECT: [
                f"'{answer_text}'的具体情况是什么？",
                f"'{answer_text}'有什么特别之处？",
                f"关于'{answer_text}'还有什么信息？"
            ],
            QuestionCategory.EVENT: [
                f"'{answer_text}'的具体时间是？",
                f"'{answer_text}'的具体地点是？",
                f"关于'{answer_text}'还有什么细节？"
            ]
        }
        
        templates = followup_templates.get(parent_category, followup_templates[QuestionCategory.EVENT])
        
        for i, q_text in enumerate(templates[:3]):
            if i == 0:
                category = QuestionCategory.PERSON
            elif i == 1:
                category = QuestionCategory.OBJECT
            else:
                category = QuestionCategory.EVENT
            
            question = Question(
                id=self._generate_question_id(),
                text=q_text,
                category=category,
                level=3,
                parent_answer_id=parent_answer_id
            )
            questions.append(question)
        
        return questions
    
    def generate_questions_for_answer(self, answer_id: str, answer_text: str, parent_category: QuestionCategory, current_level: int) -> List[Question]:
        if current_level == 1:
            return self.generate_level2_questions(answer_id, answer_text, parent_category)
        elif current_level == 2:
            return self.generate_level3_questions(answer_id, answer_text, parent_category)
        else:
            return []
