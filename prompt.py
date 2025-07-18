defstr = '''
请根据以下模型类 `TestCase` 的定义，理解用户的操作意图（主要围绕测试用例的增删改查、过滤、搜索、展示等功能），
并生成符合意图的 Python 代码，代码应清晰、实用、可直接执行。无需解释，仅返回完整代码块。

模型类如下：
class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_no = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    module_name = db.Column(db.String(100))
    function = db.Column(db.String(200))
    title = db.Column(db.String(200), nullable=False)
    user_role = db.Column(db.String(100))
    precondition = db.Column(db.Text)
    steps = db.Column(db.Text)
    expected_result = db.Column(db.Text)
    actual_result = db.Column(db.Text)
    basis = db.Column(db.Text)
    remark = db.Column(db.Text)
    create_by = db.Column(db.String(100))
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    executed_by = db.Column(db.String(100))
    execution_date = db.Column(db.DateTime)
    user_story_id = db.Column(db.Integer, db.ForeignKey('user_story.id'), nullable=False)
'''
