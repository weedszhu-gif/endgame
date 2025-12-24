
from rest_framework import serializers
from .models import Question, QuestionTag, HintRule, AnswerRecord


class QuestionTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionTag
        fields = ['tag']


class QuestionSerializer(serializers.ModelSerializer):
    tags = QuestionTagSerializer(many=True, read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'type', 'type_display', 'content', 'difficulty', 
                  'solution', 'hint_pattern', 'tags']

    def create(self, validated_data):
        # 创建题目时不处理标签，标签需要单独创建
        return Question.objects.create(**validated_data)


class HintRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HintRule
        fields = ['id', 'pattern_id', 'trigger_keywords', 'hint_text']


class AnswerRecordSerializer(serializers.ModelSerializer):
    question_type = serializers.CharField(source='question.get_type_display', read_only=True)
    question_content = serializers.CharField(source='question.content', read_only=True)

    class Meta:
        model = AnswerRecord
        fields = ['id', 'question', 'question_type', 'question_content', 
                  'student_input', 'used_hint', 'created_at']
