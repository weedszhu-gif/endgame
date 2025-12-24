
from django.db import models
from django.utils import timezone

class Question(models.Model):
    """题库表"""
    TYPE_CHOICES = (
        ('choice', '选择题'),
        ('calculation', '计算题'),
        ('proof', '证明题'),
    )

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, help_text='题型')
    content = models.TextField(help_text='题目内容（含LaTeX公式）')
    difficulty = models.PositiveSmallIntegerField(default=3, help_text='难度1-5')
    solution = models.TextField(blank=True, null=True, help_text='标准答案')
    hint_pattern = models.CharField(max_length=50, blank=True, null=True, help_text='规则引擎标识符')

    class Meta:
        db_table = 'questions'
        verbose_name = '题目'
        verbose_name_plural = '题目'

    def __str__(self):
        return f"{self.get_type_display()} - ID:{self.id}"


class QuestionTag(models.Model):
    """知识点标签表"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=50, help_text='如"二次函数","相似三角形"')

    class Meta:
        db_table = 'question_tags'
        verbose_name = '题目标签'
        verbose_name_plural = '题目标签'
        unique_together = ('question', 'tag')

    def __str__(self):
        return f"{self.question.id} - {self.tag}"


class HintRule(models.Model):
    """规则引擎表"""
    id = models.AutoField(primary_key=True)
    pattern_id = models.CharField(max_length=50, help_text='规则标识')
    trigger_keywords = models.JSONField(help_text='触发关键词数组')
    hint_text = models.TextField(help_text='提示内容')

    class Meta:
        db_table = 'hint_rules'
        verbose_name = '提示规则'
        verbose_name_plural = '提示规则'

    def __str__(self):
        return f"规则: {self.pattern_id}"


class AnswerRecord(models.Model):
    """学生答题记录表"""
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_records')
    student_input = models.TextField(help_text='学生输入步骤')
    used_hint = models.TextField(blank=True, null=True, help_text='使用的提示')
    created_at = models.DateTimeField(default=timezone.now, help_text='创建时间')

    class Meta:
        db_table = 'answer_records'
        verbose_name = '答题记录'
        verbose_name_plural = '答题记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"答题记录 - 题目ID:{self.question.id} - {self.created_at}"
