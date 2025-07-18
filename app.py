# app.py
# 1. 在顶部导入 flash
from flask import Flask, session,render_template, request, redirect, url_for, jsonify, flash,send_file,Response,stream_with_context
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import io
import pandas as pd
import xlsxwriter
from utils import chat_mode, run_python_code
from prompt import defstr
import uuid


app = Flask(__name__)
app.secret_key = 'super-secret-key-for-flash-messages'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_mgmt.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# --- Models ---
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    modules = db.relationship('Module', backref='project', cascade="all, delete-orphan")

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_stories = db.relationship('UserStory', backref='module', cascade="all, delete-orphan")

class UserStory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    test_cases = db.relationship('TestCase', backref='user_story', cascade="all, delete-orphan")

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

@app.before_request
def ensure_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())  # 生成一个唯一ID
# 这个函数会让变量 'now' 在所有模板中都可用
@app.context_processor
def inject_now():
    # Call the function to get the actual datetime object
    return {'now': datetime.utcnow()}
# --- Routes ---
@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)

@app.route('/project/<int:project_id>')
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project.html', project=project)

@app.route('/module/<int:module_id>')
def view_module(module_id):
    module = Module.query.get_or_404(module_id)
    return render_template('module.html', module=module)

@app.route('/userstory/<int:userstory_id>')
def view_userstory(userstory_id):
    userstory = UserStory.query.get_or_404(userstory_id)
    return render_template('userstory.html', userstory=userstory)


@app.route('/add_cases', methods=['GET', 'POST'])
def add_cases():
    # 先查询所有项目，关联模块和用户故事
    projects = Project.query.order_by(Project.id).all()
    grouped_user_stories = []

    for project in projects:
        modules_data = []
        for module in project.modules:  # 假设关系 Project.modules
            user_stories_data = [
                {"id": us.id, "title": us.title} for us in module.user_stories
            ]
            if user_stories_data:  # 只添加有用户故事的模块
                modules_data.append({
                    "module_name": module.name,
                    "user_stories": user_stories_data
                })

        if modules_data:  # 只添加有模块的项目
            grouped_user_stories.append({
                "project_name": project.name,
                "modules": modules_data
            })

    if request.method == 'POST':
        story_id = None
        try:
            json_data = request.form['json_input']
            story_id = int(request.form['user_story'])
            cases = json.loads(json_data)

            # 查找对应的用户故事
            user_story = UserStory.query.get(story_id)
            if not user_story:
                flash("错误：选择的用户故事不存在。", 'danger')
                return redirect(url_for('add_cases'))

            for case in cases:
                tc = TestCase(
                    case_no=case.get("Case No."),
                    priority=str(case.get("Priority")),
                    module_name=case.get("Module"),
                    function=case.get("Function"),
                    title=case.get("Test Case Name"),
                    user_role=case.get("User Role"),
                    precondition=case.get("Precondition"),
                    steps="\n".join(case.get("Test Steps", [])),
                    expected_result="\n".join(case.get("Expected Result", [])),
                    actual_result=case.get("Actual Result"),
                    basis=case.get("Basis for case preparation"),
                    remark=case.get("Remark"),
                    create_by=case.get("Create By"),
                    executed_by=case.get("Executed BY"),
                    execution_date=None if not case.get("Execution Date") else datetime.strptime(case.get("Execution Date"), "%Y-%m-%d"),
                    create_date=None if not case.get("Create Date") else datetime.strptime(case.get("Create Date"), "%Y-%m-%d"),
                    user_story_id=story_id
                )
                db.session.add(tc)

            db.session.commit()
            flash(f"成功为用户故事 '{user_story.title}' 导入了 {len(cases)} 个测试用例。", 'success')
            return redirect(url_for('view_userstory', userstory_id=story_id))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ 导入失败：{e}", 'danger')
            return redirect(url_for('add_cases'))

    return render_template('add_cases.html', grouped_user_stories=grouped_user_stories)


@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        name = request.form['name']
        db.session.add(Project(name=name))
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_project.html')

@app.route('/add_module/<int:project_id>', methods=['GET', 'POST'])
def add_module(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        name = request.form['name']
        db.session.add(Module(name=name, project=project))
        db.session.commit()
        return redirect(url_for('view_project', project_id=project_id))
    return render_template('add_module.html', project=project)

@app.route('/add_userstory/<int:module_id>', methods=['GET', 'POST'])
def add_userstory(module_id):
    module = Module.query.get_or_404(module_id)
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        db.session.add(UserStory(title=title, description=description, module=module))
        db.session.commit()
        return redirect(url_for('view_module', module_id=module_id))
    return render_template('add_userstory.html', module=module)


# 3. 添加新的删除路由
@app.route('/userstory/delete/<int:userstory_id>', methods=['POST'])
def delete_userstory(userstory_id):
    # 查找要删除的用户故事，如果不存在则返回 404
    userstory = UserStory.query.get_or_404(userstory_id)

    # 在删除对象前，先获取其父模块的 ID，以便之后重定向
    module_id = userstory.module_id
    title = userstory.title

    try:
        # 从数据库会话中删除对象
        db.session.delete(userstory)
        # 提交更改到数据库
        # 注意：因为模型中设置了 cascade="all, delete-orphan"，
        # 所以与此用户故事关联的所有测试用例也会被自动删除。
        db.session.commit()

        # 创建一个成功的 flash 消息
        flash(f"用户故事 '{title}' 已被成功删除。", 'success')

    except Exception as e:
        db.session.rollback()  # 如果出错，回滚事务
        flash(f"删除用户故事时发生错误: {e}", 'danger')

    # 重定向到该用户故事所属的模块页面
    return redirect(url_for('view_module', module_id=module_id))


@app.route('/testcase/delete/<int:test_case_id>', methods=['POST'])
def delete_test_case(test_case_id):
    # 查找要删除的测试用例，如果不存在则返回 404
    test_case = TestCase.query.get_or_404(test_case_id)

    # 在删除对象前，先获取其父用户故事的 ID，以便之后重定向
    user_story_id = test_case.user_story_id
    case_no = test_case.case_no

    try:
        # 从数据库会话中删除对象
        db.session.delete(test_case)
        # 提交更改到数据库
        db.session.commit()

        # 创建一个成功的 flash 消息
        flash(f"测试用例 '{case_no}' 已被成功删除。", 'success')

    except Exception as e:
        db.session.rollback()  # 如果出错，回滚事务
        flash(f"删除测试用例时发生错误: {e}", 'danger')

    # 重定向回该测试用例所属的用户故事页面
    return redirect(url_for('view_userstory', userstory_id=user_story_id))

# --- 新增的删除项目路由 ---
@app.route('/project/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    # 查找要删除的项目，如果不存在则返回 404
    project = Project.query.get_or_404(project_id)
    project_name = project.name # 在删除前获取项目名称，用于 flash 消息

    try:
        # 从数据库会话中删除项目对象
        # 因为模型中设置了 cascade="all, delete-orphan"，
        # 所有关联的模块、用户故事和测试用例都会被一并删除。
        db.session.delete(project)
        db.session.commit()
        flash(f"项目 '{project_name}' 及其所有内容已成功删除。", 'success')
    except Exception as e:
        db.session.rollback() # 如果出错，回滚事务
        flash(f"删除项目时发生错误: {e}", 'danger')

    # 删除成功后，重定向回项目列表首页
    return redirect(url_for('index'))

# 查看某个项目下的所有测试用例
@app.route('/project/<int:project_id>/testcases')
def view_project_testcases(project_id):
    project = Project.query.get_or_404(project_id)
    testcases = (
        db.session.query(TestCase, UserStory)
        .join(UserStory, TestCase.user_story_id == UserStory.id)
        .filter(UserStory.module.has(project_id=project_id))
        .all()
    )
    return render_template('project_testcases.html', project=project, testcases=testcases)

# 下载该项目的测试用例为 Excel
@app.route('/project/<int:project_id>/testcases/download')
def download_project_testcases(project_id):
    testcases = (
        db.session.query(TestCase, UserStory)
        .join(UserStory, TestCase.user_story_id == UserStory.id)
        .filter(UserStory.module.has(project_id=project_id))
        .all()
    )

    data = []
    for tc, us in testcases:
        data.append({
            '用例编号': tc.case_no,
            '测试标题': tc.title,
            '用户故事': us.title,
            '模块': tc.module_name,
            '功能点': tc.function,
            '优先级': tc.priority,
            '用户角色': tc.user_role,
            '前置条件': tc.precondition,
            '步骤': tc.steps,
            '预期结果': tc.expected_result,
            '实际结果': tc.actual_result,
            '依据': tc.basis,
            '备注': tc.remark,
            '创建人': tc.create_by,
            '创建时间': tc.create_date,
            '执行人': tc.executed_by,
            '执行时间': tc.execution_date,
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='TestCases')
    output.seek(0)

    return send_file(output,
                     as_attachment=True,
                     download_name=f'Project_{project_id}_TestCases.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/init_db')
def init_db():
    db.drop_all()
    db.create_all()

    project = Project(name='测试')
    db.session.add(project)

    for i in range(1, 4):
        module = Module(name=f'功能模块{i}', project=project)
        db.session.add(module)

        for j in range(1, 4):
            us = UserStory(title=f'模块{i}-用户故事{j}', description=f'描述 模块{i} 用户故事{j}', module=module)
            db.session.add(us)

            for k in range(1, 3):
                tc = TestCase(
                    case_no=f'TC{i}{j}{k}',
                    priority='High' if k == 1 else 'Medium',
                    module_name=module.name,
                    function=f'功能点{i}-{j}',
                    title=f'US{i}-{j} 用例{k}',
                    user_role='测试角色A',
                    precondition='用户已登录',
                    steps=f'步骤：执行第{k}步',
                    expected_result=f'预期结果{k}',
                    actual_result='',
                    basis='需求文档章节1.2',
                    remark='初始测试用例',
                    create_by='系统生成',
                    executed_by='',
                    execution_date=None,
                    user_story=us
                )
                db.session.add(tc)

    db.session.commit()
    return "数据库初始化完成！"
chat_history_store = {}  # 示例结构：{session_id: [messages]}
MAX_TURNS = 5  # 每轮用户+AI，共20条消息（如果严格按“轮”来计）

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages')
    stream = data.get('stream', False)
    session_id = session.get('session_id')
    userstory_id = data.get("userstory_id")

    if not userstory_id:
        return jsonify({"error": "Missing userstory_id"}), 400

    if not messages:
        return jsonify({"error": "messages is required"}), 400
        # 查询当前用户故事
    user_story = UserStory.query.get(userstory_id)
    if not user_story:
        return jsonify({"error": "User story not found"}), 404

    # 获取该用户故事下的所有测试用例
    test_cases = user_story.test_cases  # ORM 关系已经定义好了
        # 举例：你可以打印调试，或者将用例内容组合起来用于AI回答
    summary = "\n".join([
        json.dumps({
            "id": tc.id,
            "case_no": tc.case_no,
            "title": tc.title,
            "priority": tc.priority,
            "module_name": tc.module_name,
            "function": tc.function,
            "user_role": tc.user_role,
            "precondition": tc.precondition,
            "steps": tc.steps,
            "expected_result": tc.expected_result,
            "actual_result": tc.actual_result,
            "basis": tc.basis,
            "remark": tc.remark,
            "create_by": tc.create_by,
            "create_date": tc.create_date.strftime('%Y-%m-%d') if tc.create_date else None,
            "executed_by": tc.executed_by,
            "execution_date": tc.execution_date.strftime('%Y-%m-%d') if tc.execution_date else None,
            "user_story_id": tc.user_story_id
        }, ensure_ascii=False)
        for tc in test_cases
    ])
    # 获取最新用户发言
    last_message = messages[-1]
    user_input = last_message.get('content', '')

    # 获取历史，如果没有则初始化为空列表
    history = chat_history_store.setdefault(session_id, [{'role': 'assistant', 'content': f'当前所有的测试用例：{summary}'}])

    # 追加当前用户发言到历史中
    history.append({"role": "user", "content": user_input})

    # 命中关键词则添加提示 prompt1
    # if any(keyword in user_input.lower() for keyword in ["用例", "case", "优化"]):
    #     prompt1 = {'role': 'assistant', 'content': defstr}
    #     history.append(prompt1)

    # 保持历史最多为 10 条对话（用户+AI）
    if len(history) > MAX_TURNS * 2:
        chat_history_store[session_id] = history[-MAX_TURNS * 2:]

    if stream:
        generator, result_holder = chat_mode(history, stream=True)

        def generate():
            for chunk in generator:
                yield f"{chunk}"
            print(result_holder['text'])

        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    else:
        result = chat_mode(history, stream=False)
        return jsonify({"response": result})



if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5066, debug=True)