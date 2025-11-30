from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
# 设置密钥，用于加密session
app.secret_key = 'your-secret-key-here'  # 生产环境中应使用更复杂的密钥

# 配置session持久化
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 设置session过期时间为7天

# 数据文件路径
DATA_FILE = 'data/posts.json'
USERS_FILE = 'data/users.json'
BOARDS_FILE = 'data/boards.json'

# 确保数据文件存在
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'posts': []}, f, ensure_ascii=False, indent=4)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'users': []}, f, ensure_ascii=False, indent=4)

if not os.path.exists(BOARDS_FILE):
    # 初始板块列表
    initial_boards = {
        'boards': [
            {
                'id': 1,
                'name': 'general',
                'display_name': '综合板块',
                'description': '综合讨论区',
                'posts_count': 0,
                'likes_count': 0,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'id': 2,
                'name': 'mc_server',
                'display_name': 'MC服务器板块',
                'description': 'Minecraft服务器讨论',
                'posts_count': 0,
                'likes_count': 0,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'id': 3,
                'name': 'python',
                'display_name': 'Python板块',
                'description': 'Python编程讨论',
                'posts_count': 0,
                'likes_count': 0,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'id': 4,
                'name': 'mc_daily',
                'display_name': 'MC日常板块',
                'description': 'Minecraft日常分享',
                'posts_count': 0,
                'likes_count': 0,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'id': 5,
                'name': 'linux',
                'display_name': 'Linux板块',
                'description': 'Linux系统讨论',
                'posts_count': 0,
                'likes_count': 0,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
    }
    with open(BOARDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(initial_boards, f, ensure_ascii=False, indent=4)

# 读取所有板块
def get_boards():
    with open(BOARDS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['boards']

# 保存板块
def save_boards(boards):
    with open(BOARDS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'boards': boards}, f, ensure_ascii=False, indent=4)

# 根据名称获取板块
def get_board_by_name(name):
    boards = get_boards()
    for board in boards:
        if board['name'] == name:
            return board
    return None

# 更新板块统计信息
def update_board_stats():
    posts = get_posts()
    boards = get_boards()
    
    # 初始化板块统计
    for board in boards:
        board['posts_count'] = 0
        board['likes_count'] = 0
    
    # 统计每个板块的帖子数和点赞数
    for post in posts:
        board_name = post.get('board', 'general')
        for board in boards:
            if board['name'] == board_name:
                board['posts_count'] += 1
                board['likes_count'] += post['likes']
                break
    
    # 保存更新后的板块数据
    save_boards(boards)

# 根据ID获取板块
def get_board_by_id(board_id):
    boards = get_boards()
    for board in boards:
        if board['id'] == board_id:
            return board
    return None

# 编辑板块信息 - 仅站长可访问
@app.route('/admin/board/edit/<int:board_id>', methods=['GET', 'POST'])
def edit_board(board_id):
    # 检查用户是否登录且为站长
    if 'user_id' not in session or session.get('role') != 'owner':
        return redirect(url_for('index'))
    
    board = get_board_by_id(board_id)
    if not board:
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        # 获取表单数据
        name = request.form.get('name')
        display_name = request.form.get('display_name')
        description = request.form.get('description')
        
        if not name or not display_name:
            return redirect(url_for('edit_board', board_id=board_id))
        
        # 更新板块信息
        boards = get_boards()
        for b in boards:
            if b['id'] == board_id:
                b['name'] = name
                b['display_name'] = display_name
                b['description'] = description
                break
        
        # 保存更新后的板块数据
        save_boards(boards)
        
        return redirect(url_for('admin'))
    
    return render_template('admin.html', boards=get_boards(), users=get_users(), edit_board=board, current_role=session.get('role'))

# 删除板块 - 仅站长可访问
@app.route('/admin/board/delete/<int:board_id>', methods=['POST'])
def delete_board(board_id):
    # 检查用户是否登录且为站长
    if 'user_id' not in session or session.get('role') != 'owner':
        return redirect(url_for('index'))
    
    # 获取板块
    board = get_board_by_id(board_id)
    if not board:
        return redirect(url_for('admin'))
    
    # 不允许删除默认板块
    if board['name'] == 'general':
        return redirect(url_for('admin'))
    
    # 获取所有帖子
    posts = get_posts()
    
    # 将该板块的帖子移到默认板块
    for post in posts:
        if post.get('board') == board['name']:
            post['board'] = 'general'
    
    # 保存更新后的帖子数据
    save_posts(posts)
    
    # 删除板块
    boards = get_boards()
    boards = [b for b in boards if b['id'] != board_id]
    
    # 保存更新后的板块数据
    save_boards(boards)
    
    # 更新板块统计
    update_board_stats()
    
    return redirect(url_for('admin'))

# 密码哈希函数
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 读取所有用户
def get_users():
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['users']

# 保存用户
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'users': users}, f, ensure_ascii=False, indent=4)

# 根据用户名获取用户列表
def get_users_by_username(username):
    users = get_users()
    return [user for user in users if user['username'] == username]

# 根据用户名获取单个用户（兼容旧代码）
def get_user_by_username(username):
    users = get_users_by_username(username)
    return users[0] if users else None

# 根据ID获取用户
def get_user_by_id(user_id):
    users = get_users()
    for user in users:
        if user['id'] == user_id:
            return user
    return None

# 读取所有帖子
def get_posts():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['posts']

# 保存帖子
def save_posts(posts):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'posts': posts}, f, ensure_ascii=False, indent=4)

# 获取单个帖子
def get_post(post_id):
    posts = get_posts()
    for post in posts:
        if post['id'] == post_id:
            return post
    return None

# 首页 - 显示所有帖子
@app.route('/')
def index():
    posts = get_posts()
    
    # 只显示已通过审核的帖子，管理员和审核员可以看到所有帖子
    role = session.get('role')
    if role not in ['owner', 'admin', 'reviewer', 'moderator']:
        posts = [post for post in posts if post.get('status') == 'approved']
    
    # 获取板块参数
    board = request.args.get('board')
    
    # 筛选板块
    if board:
        posts = [post for post in posts if post.get('board') == board]
    
    # 获取排序参数
    sort_by = request.args.get('sort', 'newest')
    
    # 根据排序参数排序
    if sort_by == 'likes':
        # 按点赞数倒序排列
        posts.sort(key=lambda x: x['likes'], reverse=True)
    elif sort_by == 'views':
        # 按浏览量倒序排列
        posts.sort(key=lambda x: x['views'], reverse=True)
    else:
        # 默认按创建时间倒序排列
        posts.sort(key=lambda x: x['created_at'], reverse=True)
    
    # 更新板块统计信息
    update_board_stats()
    
    return render_template('index.html', posts=posts, current_role=role)

# 搜索功能
@app.route('/search')
def search():
    # 获取搜索关键词
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('index'))
    
    # 获取所有帖子
    posts = get_posts()
    
    # 只显示已通过审核的帖子，管理员和审核员可以看到所有帖子
    role = session.get('role')
    if role not in ['owner', 'admin', 'reviewer', 'moderator']:
        posts = [post for post in posts if post.get('status') == 'approved']
    
    # 搜索帖子标题和内容
    results = []
    for post in posts:
        # 检查标题或内容是否包含搜索关键词
        if query.lower() in post['title'].lower() or query.lower() in post['content'].lower():
            results.append(post)
    
    # 按创建时间倒序排列
    results.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('search.html', posts=results, query=query, current_role=role)

# 获取所有帖子的JSON数据
@app.route('/posts')
def posts_json():
    posts = get_posts()
    posts.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify(posts)

# 帖子详情页
@app.route('/post/<int:post_id>')
def post_detail(post_id):
    posts = get_posts()
    post = None
    for p in posts:
        if p['id'] == post_id:
            post = p
            break
    
    if not post:
        return '帖子不存在', 404
    
    # 检查帖子状态，普通用户只能访问已通过审核的帖子
    role = session.get('role')
    if role not in ['owner', 'admin', 'reviewer'] and post.get('status') != 'approved':
        return '帖子正在审核中或已被拒绝', 403
    
    # 增加浏览量
    post['views'] += 1
    save_posts(posts)
    
    return render_template('post.html', post=post, current_role=role)

# 获取单个帖子的JSON数据
@app.route('/post/<int:post_id>/json')
def post_json(post_id):
    post = get_post(post_id)
    if not post:
        return jsonify({'error': '帖子不存在'}), 404
    return jsonify(post)

# 注册页面
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

# 注册API
@app.route('/register', methods=['POST'])
def register():
    # 获取表单数据
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # 验证数据
    if not username or not password or not confirm_password:
        return jsonify({'error': '用户名、密码和确认密码不能为空'}), 400
    
    if password != confirm_password:
        return jsonify({'error': '两次输入的密码不一致'}), 400
    
    # 允许重复用户名，移除唯一性检查
    
    # 生成新用户ID
    users = get_users()
    new_id = max([user['id'] for user in users], default=0) + 1
    
    # 创建新用户，默认角色为普通用户
        new_user = {
            'id': new_id,
            'username': username,
            'password': hash_password(password),
            'email': '',
            'qq': '',
            'age': '',
            'gender': '',
            'introduction': '',
            'role': 'user',  # 默认角色为普通用户
            'managed_boards': [],  # 版主管理的板块列表，仅版主角色使用
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'banned': False  # 用户封禁状态
        }
    
    # 保存用户
    users.append(new_user)
    save_users(users)
    
    # 注册成功后自动登录
    session.permanent = True  # 设置session为永久
    session['user_id'] = new_id
    session['username'] = username
    session['role'] = 'user'  # 注册用户默认角色为普通用户
    
    return jsonify({'success': True, 'redirect': '/'})

# 登录页面
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# 获取同名用户列表
@app.route('/users/<username>')
def get_users_by_name(username):
    users = get_users()
    matched_users = [user for user in users if user['username'] == username]
    return jsonify({'users': matched_users})

# 获取所有用户（用于搜索）
@app.route('/users')
def get_all_users():
    users = get_users()
    return jsonify({'users': users})

# 登录API
@app.route('/login', methods=['POST'])
def login():
    # 获取表单数据
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    
    # 验证数据
    if not user_id or not password:
        return jsonify({'error': '用户ID和密码不能为空'}), 400
    
    # 根据ID获取用户
    user = get_user_by_id(int(user_id))
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # 检查用户是否被封禁
    if user.get('banned', False):
        return jsonify({'error': '您的账号已被封禁'}), 403
    
    # 验证密码
    if user['password'] != hash_password(password):
        return jsonify({'error': '密码错误'}), 400
    
    # 登录成功，设置session
    session.permanent = True  # 设置session为永久
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user.get('role', 'user')  # 保存用户角色
    return jsonify({'success': True, 'redirect': '/'})

# 退出登录
@app.route('/logout')
def logout():
    # 清除session
    session.clear()
    return redirect(url_for('index'))

# 管理页面 - 仅管理员和版主可访问
@app.route('/admin')
def admin():
    # 检查用户是否登录
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    # 获取用户角色
    role = session.get('role')
    
    # 只有管理员、版主、审核员或站长可以访问管理页面
    if role not in ['owner', 'admin', 'moderator', 'reviewer']:
        return redirect(url_for('index'))
    
    # 获取所有用户和板块数据
    users = get_users()
    boards = get_boards()
    
    return render_template('admin.html', users=users, boards=boards, current_role=role)

# 更新用户角色和管理板块 - 仅管理员可访问
@app.route('/admin/update_user_role', methods=['POST'])
def update_user_role():
    # 检查用户是否登录且为管理员或站长
    if 'user_id' not in session or session.get('role') not in ['owner', 'admin']:
        return redirect(url_for('index'))
    
    # 获取表单数据
    user_id = request.form.get('user_id')
    role = request.form.get('role')
    managed_boards = request.form.getlist('managed_boards')  # 获取多选框的值
    
    # 验证数据
    if not user_id or not role:
        return redirect(url_for('admin'))
    
    # 获取所有用户
    users = get_users()
    
    # 查找并更新用户
    for user in users:
        if user['id'] == int(user_id):
            user['role'] = role
            # 只有版主需要管理板块
            if role == 'moderator':
                user['managed_boards'] = managed_boards
            else:
                user['managed_boards'] = []
            break
    
    # 保存更新后的用户数据
    save_users(users)
    
    return redirect(url_for('admin'))

# 删除用户 - 仅站长可访问
@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # 检查用户是否登录且为站长
    if 'user_id' not in session or session.get('role') != 'owner':
        return redirect(url_for('index'))
    
    # 不允许删除自己
    if session['user_id'] == user_id:
        return redirect(url_for('admin'))
    
    # 获取所有用户
    users = get_users()
    
    # 删除用户
    users = [user for user in users if user['id'] != user_id]
    
    # 保存更新后的用户数据
    save_users(users)
    
    return redirect(url_for('admin'))

# 封禁/解封用户 - 仅站长可访问
@app.route('/admin/user/ban/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    # 检查用户是否登录且为站长
    if 'user_id' not in session or session.get('role') != 'owner':
        return redirect(url_for('index'))
    
    # 不允许封禁自己
    if session['user_id'] == user_id:
        return redirect(url_for('admin'))
    
    # 获取所有用户
    users = get_users()
    
    # 切换用户封禁状态
    for user in users:
        if user['id'] == user_id:
            user['banned'] = not user.get('banned', False)
            break
    
    # 保存更新后的用户数据
    save_users(users)
    
    return redirect(url_for('admin'))

# 增加帖子浏览量
@app.route('/post/<int:post_id>/view')
def increment_view(post_id):
    posts = get_posts()
    for post in posts:
        if post['id'] == post_id:
            post['views'] += 1
            save_posts(posts)
            return jsonify({'success': True, 'views': post['views']})
    return jsonify({'error': '帖子不存在'}), 404

# 点赞/取消点赞帖子
@app.route('/post/<int:post_id>/like', methods=['GET', 'POST'])
def like_post(post_id):
    # 检查用户是否登录
    if 'user_id' not in session:
        if request.method == 'POST':
            # 如果是POST请求，重定向到登录页
            return redirect(url_for('login_page'))
        return jsonify({'success': False, 'error': '请先登录'}), 401
    
    current_user = session['username']
    posts = get_posts()
    
    for post in posts:
        if post['id'] == post_id:
            # 检查用户是否已经点赞
            if current_user in post['liked_by']:
                # 取消点赞
                post['likes'] -= 1
                post['liked_by'].remove(current_user)
            else:
                # 点赞
                post['likes'] += 1
                post['liked_by'].append(current_user)
            
            # 保存到数据文件
            save_posts(posts)
            
            if request.method == 'POST':
                # 如果是POST请求，重定向回帖子详情页
                return redirect(url_for('post_detail', post_id=post_id))
            return jsonify({'success': True, 'likes': post['likes'], 'liked': current_user in post['liked_by']})
    
    if request.method == 'POST':
        # 如果是POST请求，重定向到首页
        return redirect(url_for('index'))
    return jsonify({'success': False, 'error': '帖子不存在'}), 404

# 添加评论
@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    # 检查用户是否登录
    if 'user_id' not in session:
        # 重定向到登录页
        return redirect(url_for('login_page'))
    
    # 获取评论内容
    content = request.form.get('content')
    if not content:
        # 重定向回帖子详情页
        return redirect(url_for('post_detail', post_id=post_id))
    
    posts = get_posts()
    for post in posts:
        if post['id'] == post_id:
            # 生成评论ID
            comment_id = max([comment.get('id', 0) for comment in post['comments']], default=0) + 1
            
            # 创建新评论
            new_comment = {
                'id': comment_id,
                'content': content,
                'author': session['username'],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 添加到帖子评论列表
            post['comments'].append(new_comment)
            save_posts(posts)
            
            # 重定向回帖子详情页
            return redirect(url_for('post_detail', post_id=post_id))
    
    # 帖子不存在，重定向到首页
    return redirect(url_for('index'))

# 创建新帖子
@app.route('/post', methods=['POST'])
def create_post():
    # 检查用户是否登录
    if 'user_id' not in session:
        return jsonify({'error': '请先登录'}), 401
    
    # 获取表单数据
    title = request.form.get('title')
    content = request.form.get('content')
    board = request.form.get('board', 'general')
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    # 生成新帖子ID
    posts = get_posts()
    new_id = max([post['id'] for post in posts], default=0) + 1
    
    # 创建新帖子
    new_post = {
        'id': new_id,
        'title': title,
        'content': content,
        'author': session['username'],
        'author_id': session['user_id'],
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'views': 0,
        'likes': 0,
        'liked_by': [],
        'comments': [],
        'board': board,
        'status': 'pending'  # 审核状态：pending(审核中), approved(已通过), rejected(已拒绝)
    }
    
    # 保存到数据文件
    posts.append(new_post)
    save_posts(posts)
    
    # 更新板块统计
    update_board_stats()
    
    # 重定向到首页
    return jsonify({'success': True, 'redirect': '/'})

# 用户个人资料页面
@app.route('/user')
def user_profile():
    # 检查用户是否登录
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    # 获取当前用户信息
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    
    if not user:
        return redirect(url_for('login_page'))
    
    return render_template('user.html', user=user)

# 编辑个人资料页面
@app.route('/user/edit')
def edit_profile():
    # 检查用户是否登录
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    # 获取当前用户信息
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    
    if not user:
        return redirect(url_for('login_page'))
    
    return render_template('edit_profile.html', user=user)

# 更新个人资料API
@app.route('/user/update', methods=['POST'])
def update_profile():
    # 检查用户是否登录
    if 'user_id' not in session:
        return jsonify({'error': '请先登录'}), 401
    
    # 获取当前用户信息
    user_id = session['user_id']
    users = get_users()
    
    # 查找用户
    for user in users:
        if user['id'] == user_id:
            # 更新用户信息
            user['email'] = request.form.get('email', '')
            user['qq'] = request.form.get('qq', '')
            user['age'] = request.form.get('age', '')
            user['gender'] = request.form.get('gender', '')
            user['introduction'] = request.form.get('introduction', '')
            break
    
    # 保存更新后的用户数据
    save_users(users)
    
    return redirect(url_for('user_profile'))

# 审核页面 - 仅管理员、审核员和版主可访问
@app.route('/review')
def review():
    # 检查用户是否登录且为管理员、审核员、版主或站长
    if 'user_id' not in session or session.get('role') not in ['owner', 'admin', 'reviewer', 'moderator']:
        return redirect(url_for('index'))
    
    # 获取所有帖子
    posts = get_posts()
    
    # 获取状态筛选参数
    status = request.args.get('status')
    
    # 根据状态筛选帖子
    if status:
        posts = [post for post in posts if post.get('status') == status]
    
    # 按创建时间倒序排列，最新的帖子在最前面
    posts.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('review.html', posts=posts, status=status)

# 审核帖子 - 仅管理员、审核员和版主可访问
@app.route('/review/<int:post_id>/<action>', methods=['POST'])
def review_post(post_id, action):
    # 检查用户是否登录且为管理员、审核员、版主或站长
    if 'user_id' not in session or session.get('role') not in ['owner', 'admin', 'reviewer', 'moderator']:
        return redirect(url_for('index'))
    
    # 验证操作类型
    if action not in ['approve', 'reject']:
        return redirect(url_for('review'))
    
    # 获取所有帖子
    posts = get_posts()
    
    # 查找并更新帖子状态
    for post in posts:
        if post['id'] == post_id:
            post['status'] = 'approved' if action == 'approve' else 'rejected'
            break
    
    # 保存更新后的帖子数据
    save_posts(posts)
    
    # 更新板块统计
    update_board_stats()
    
    return redirect(url_for('review'))

# 删除帖子 - 仅管理员、审核员和版主可访问
@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    # 检查用户是否登录且为管理员、审核员、版主或站长
    if 'user_id' not in session or session.get('role') not in ['owner', 'admin', 'reviewer', 'moderator']:
        return redirect(url_for('index'))
    
    # 获取所有帖子
    posts = get_posts()
    
    # 查找并删除帖子
    posts = [post for post in posts if post['id'] != post_id]
    
    # 保存更新后的帖子数据
    save_posts(posts)
    
    # 更新板块统计
    update_board_stats()
    
    # 重定向到首页
    return redirect(url_for('index'))

# 隐藏/显示帖子 - 仅管理员、审核员和版主可访问
@app.route('/post/<int:post_id>/hide', methods=['POST'])
def hide_post(post_id):
    # 检查用户是否登录且为管理员、审核员、版主或站长
    if 'user_id' not in session or session.get('role') not in ['owner', 'admin', 'reviewer', 'moderator']:
        return redirect(url_for('index'))
    
    # 获取所有帖子
    posts = get_posts()
    
    # 查找并更新帖子状态
    for post in posts:
        if post['id'] == post_id:
            # 切换帖子状态
            if post['status'] == 'approved':
                post['status'] = 'rejected'  # 隐藏帖子
            else:
                post['status'] = 'approved'  # 显示帖子
            break
    
    # 保存更新后的帖子数据
    save_posts(posts)
    
    # 更新板块统计
    update_board_stats()
    
    # 重定向回帖子详情页
    return redirect(url_for('post_detail', post_id=post_id))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)