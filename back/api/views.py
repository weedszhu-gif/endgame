
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Question, QuestionTag, HintRule, AnswerRecord
from .serializers import (
    QuestionSerializer, 
    QuestionTagSerializer, 
    HintRuleSerializer, 
    AnswerRecordSerializer
)


class QuestionViewSet(viewsets.ModelViewSet):
    """题目管理视图集"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'difficulty']
    search_fields = ['content', 'solution']
    ordering_fields = ['id', 'difficulty', 'created_at']
    ordering = ['-id']

    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        """为题目添加标签"""
        question = self.get_object()
        tag = request.data.get('tag')

        if not tag:
            return Response(
                {'error': '标签内容不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查标签是否已存在
        if QuestionTag.objects.filter(question=question, tag=tag).exists():
            return Response(
                {'error': '该标签已存在'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建新标签
        question_tag = QuestionTag.objects.create(question=question, tag=tag)
        serializer = QuestionTagSerializer(question_tag)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def remove_tag(self, request, pk=None):
        """删除题目标签"""
        question = self.get_object()
        tag = request.data.get('tag')

        if not tag:
            return Response(
                {'error': '标签内容不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            question_tag = QuestionTag.objects.get(question=question, tag=tag)
            question_tag.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except QuestionTag.DoesNotExist:
            return Response(
                {'error': '标签不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class HintRuleViewSet(viewsets.ModelViewSet):
    """提示规则管理视图集"""
    queryset = HintRule.objects.all()
    serializer_class = HintRuleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['pattern_id']
    search_fields = ['pattern_id', 'hint_text']

    @action(detail=False, methods=['post'])
    def get_hint(self, request):
        """根据学生输入和题目获取提示"""
        question_id = request.data.get('question_id')
        student_input = request.data.get('student_input')

        if not question_id or not student_input:
            return Response(
                {'error': '题目ID和学生输入不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response(
                {'error': '题目不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # 如果题目有hint_pattern，查找对应的规则
        if question.hint_pattern:
            try:
                hint_rule = HintRule.objects.get(pattern_id=question.hint_pattern)
                # 简单的关键词匹配
                trigger_keywords = hint_rule.trigger_keywords
                matched_keywords = [
                    kw for kw in trigger_keywords 
                    if kw.lower() in student_input.lower()
                ]

                if matched_keywords:
                    return Response({
                        'hint': hint_rule.hint_text,
                        'matched_keywords': matched_keywords
                    })
            except HintRule.DoesNotExist:
                pass

        return Response({'hint': None, 'matched_keywords': []})


class AnswerRecordViewSet(viewsets.ModelViewSet):
    """答题记录管理视图集"""
    queryset = AnswerRecord.objects.all()
    serializer_class = AnswerRecordSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['question']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def create(self, request, *args, **kwargs):
        """创建答题记录时，可能需要获取提示"""
        question_id = request.data.get('question')
        student_input = request.data.get('student_input')

        # 如果需要获取提示
        if request.data.get('get_hint', False) and question_id and student_input:
            try:
                question = Question.objects.get(id=question_id)
                if question.hint_pattern:
                    try:
                        hint_rule = HintRule.objects.get(pattern_id=question.hint_pattern)
                        trigger_keywords = hint_rule.trigger_keywords
                        matched_keywords = [
                            kw for kw in trigger_keywords 
                            if kw.lower() in student_input.lower()
                        ]

                        if matched_keywords:
                            # 更新请求中的提示内容
                            request.data['used_hint'] = hint_rule.hint_text
                    except HintRule.DoesNotExist:
                        pass
            except Question.DoesNotExist:
                pass

        return super().create(request, *args, **kwargs)
