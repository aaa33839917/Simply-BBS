// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 获取发帖表单
    const postForm = document.getElementById('postForm');
    // 获取登录表单
    const loginForm = document.getElementById('loginForm');
    // 获取注册表单
    const registerForm = document.getElementById('registerForm');
    // 获取点赞按钮
    const likeBtn = document.getElementById('like-btn');
    // 获取评论表单
    const commentForm = document.getElementById('commentForm');
    
    // 如果表单存在，添加提交事件监听
    if (postForm) {
        postForm.addEventListener('submit', handlePostFormSubmit);
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegisterFormSubmit);
    }
    
    // 如果是帖子详情页，增加浏览量
    if (likeBtn) {
        console.log('找到点赞按钮，绑定点击事件');
        const postId = likeBtn.dataset.postId;
        console.log('帖子ID:', postId);
        // 移除旧的事件监听，防止重复绑定
        likeBtn.removeEventListener('click', handleLike);
        // 绑定新的事件监听
        likeBtn.addEventListener('click', handleLike);
        console.log('点赞按钮事件监听已绑定');
    } else {
        console.log('未找到点赞按钮');
    }
    
    // 如果是帖子详情页，添加评论表单提交事件
    if (commentForm) {
        commentForm.addEventListener('submit', handleCommentSubmit);
    }
    
    // 登录流程处理
    initLoginFlow();
});

// 初始化登录流程
function initLoginFlow() {
    // 获取DOM元素
    const step0 = document.getElementById('step0');
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const step4 = document.getElementById('step4');
    const nameLoginBtn = document.getElementById('nameLoginBtn');
    const idLoginBtn = document.getElementById('idLoginBtn');
    const usernameForm = document.getElementById('usernameForm');
    const idLoginForm = document.getElementById('idLoginForm');
    const backBtn = document.getElementById('backBtn');
    const backToSelectBtn = document.getElementById('backToSelect');
    const backToOption1 = document.getElementById('backToOption1');
    const backToOption2 = document.getElementById('backToOption2');
    const usersList = document.getElementById('usersList');
    const idSearch = document.getElementById('idSearch');
    const passwordForm = document.getElementById('passwordForm');
    
    // 登录方式选择按钮事件
    if (nameLoginBtn) {
        nameLoginBtn.addEventListener('click', () => {
            step0.classList.remove('active');
            step1.classList.add('active');
        });
    }
    
    if (idLoginBtn) {
        idLoginBtn.addEventListener('click', () => {
            step0.classList.remove('active');
            step4.classList.add('active');
        });
    }
    
    // 用户名表单提交事件
    if (usernameForm) {
        usernameForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const username = document.getElementById('username').value;
            
            // 获取同名用户列表
            const users = await getUsersByUsername(username);
            
            if (users.length === 0) {
                alert('用户名不存在');
                return;
            }
            
            // 显示用户列表
            displayUsersList(users);
            
            // 切换到步骤2
            step1.classList.remove('active');
            step2.classList.add('active');
        });
    }
    
    // ID登录表单提交事件
    if (idLoginForm) {
        idLoginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            try {
                // 发送登录请求
                const response = await fetch('/login', {
                    method: 'POST',
                    body: new FormData(event.target)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // 成功后重定向到首页
                    window.location.href = result.redirect;
                } else {
                    alert('登录失败：' + result.error);
                }
            } catch (error) {
                console.error('登录时发生错误：', error);
                alert('登录失败，请检查网络连接后重试');
            }
        });
    }
    
    // 返回按钮事件
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            step2.classList.remove('active');
            step1.classList.add('active');
        });
    }
    
    // 返回选择按钮事件
    if (backToSelectBtn) {
        backToSelectBtn.addEventListener('click', () => {
            step3.classList.remove('active');
            step2.classList.add('active');
        });
    }
    
    // 返回登录方式选择按钮事件
    if (backToOption1) {
        backToOption1.addEventListener('click', () => {
            step1.classList.remove('active');
            step0.classList.add('active');
        });
    }
    
    if (backToOption2) {
        backToOption2.addEventListener('click', () => {
            step4.classList.remove('active');
            step0.classList.add('active');
        });
    }
    
    // ID搜索事件
    if (idSearch) {
        idSearch.addEventListener('input', () => {
            const searchTerm = idSearch.value;
            filterUsersList(searchTerm);
        });
    }
    
    // 密码表单提交事件
    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordSubmit);
    }
}

// 根据用户名获取用户列表
async function getUsersByUsername(username) {
    try {
        const response = await fetch(`/users/${username}`);
        const result = await response.json();
        return result.users || [];
    } catch (error) {
        console.error('获取用户列表失败：', error);
        return [];
    }
}

// 显示用户列表
function displayUsersList(users) {
    const usersList = document.getElementById('usersList');
    usersList.innerHTML = '';
    
    users.forEach(user => {
        const userItem = document.createElement('div');
        userItem.className = 'user-item';
        userItem.dataset.userId = user.id;
        userItem.dataset.username = user.username;
        
        userItem.innerHTML = `
            <div class="user-info">
                <span class="user-name">${user.username}</span>
                <span class="user-id">ID: ${user.id}</span>
            </div>
            <div class="user-created">创建时间: ${user.created_at}</div>
        `;
        
        // 添加点击事件
        userItem.addEventListener('click', () => {
            selectUser(user.id, user.username);
        });
        
        usersList.appendChild(userItem);
    });
    
    // 保存当前用户列表
    usersList.dataset.users = JSON.stringify(users);
}

// 选择用户
function selectUser(userId, username) {
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const selectedUsername = document.getElementById('selectedUsername');
    const selectedUserId = document.getElementById('selectedUserId');
    const selectedUser = document.getElementById('selectedUser');
    
    // 更新选择信息
    selectedUsername.textContent = username;
    selectedUserId.textContent = userId;
    selectedUser.value = userId;
    
    // 切换到步骤3
    step2.classList.remove('active');
    step3.classList.add('active');
}

// 过滤用户列表
function filterUsersList(searchTerm) {
    const usersList = document.getElementById('usersList');
    const users = JSON.parse(usersList.dataset.users || '[]');
    
    let filteredUsers = users;
    
    if (searchTerm) {
        filteredUsers = users.filter(user => {
            return user.id.toString().includes(searchTerm);
        });
    }
    
    // 重新渲染用户列表
    usersList.innerHTML = '';
    filteredUsers.forEach(user => {
        const userItem = document.createElement('div');
        userItem.className = 'user-item';
        userItem.dataset.userId = user.id;
        userItem.dataset.username = user.username;
        
        userItem.innerHTML = `
            <div class="user-info">
                <span class="user-name">${user.username}</span>
                <span class="user-id">ID: ${user.id}</span>
            </div>
            <div class="user-created">创建时间: ${user.created_at}</div>
        `;
        
        // 添加点击事件
        userItem.addEventListener('click', () => {
            selectUser(user.id, user.username);
        });
        
        usersList.appendChild(userItem);
    });
}

// 密码表单提交
async function handlePasswordSubmit(event) {
    event.preventDefault();
    
    const userId = document.getElementById('selectedUser').value;
    const password = document.getElementById('password').value;
    
    try {
        // 发送登录请求
        const response = await fetch('/login', {
            method: 'POST',
            body: new FormData(event.target)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 成功后重定向到首页
            window.location.href = result.redirect;
        } else {
            alert('登录失败：' + result.error);
        }
    } catch (error) {
        console.error('登录时发生错误：', error);
        alert('登录失败，请检查网络连接后重试');
    }
}

// 处理发帖表单提交
async function handlePostFormSubmit(event) {
    // 阻止表单默认提交行为
    event.preventDefault();
    
    // 获取表单数据
    const formData = new FormData(event.target);
    
    try {
        // 发送POST请求到后端API
        const response = await fetch('/post', {
            method: 'POST',
            body: formData
        });
        
        // 解析响应数据
        const result = await response.json();
        
        // 处理响应结果
        if (result.success) {
            // 成功后重定向到首页
            window.location.href = result.redirect;
        } else {
            // 显示错误信息
            alert('发布失败：' + result.error);
        }
    } catch (error) {
        // 处理网络错误
        console.error('发布帖子时发生错误：', error);
        alert('发布失败，请检查网络连接后重试');
    }
}

// 处理登录表单提交（兼容旧版登录）
async function handleLoginFormSubmit(event) {
    // 阻止表单默认提交行为
    event.preventDefault();
    
    // 获取表单数据
    const formData = new FormData(event.target);
    
    try {
        // 发送POST请求到后端API
        const response = await fetch('/login', {
            method: 'POST',
            body: formData
        });
        
        // 解析响应数据
        const result = await response.json();
        
        // 处理响应结果
        if (result.success) {
            // 成功后重定向到首页
            window.location.href = result.redirect;
        } else {
            alert('登录失败：' + result.error);
        }
    } catch (error) {
        console.error('登录时发生错误：', error);
        alert('登录失败，请检查网络连接后重试');
    }
}

// 处理注册表单提交
async function handleRegisterFormSubmit(event) {
    // 阻止表单默认提交行为
    event.preventDefault();
    
    // 获取表单数据
    const formData = new FormData(event.target);
    
    try {
        // 发送POST请求到后端API
        const response = await fetch('/register', {
            method: 'POST',
            body: formData
        });
        
        // 解析响应数据
        const result = await response.json();
        
        // 处理响应结果
        if (result.success) {
            // 成功后重定向到首页
            window.location.href = result.redirect;
        } else {
            alert('注册失败：' + result.error);
        }
    } catch (error) {
        console.error('注册时发生错误：', error);
        alert('注册失败，请检查网络连接后重试');
    }
}

// 增加浏览量
async function incrementView(postId) {
    try {
        await fetch(`/post/${postId}/view`);
    } catch (error) {
        console.error('增加浏览量失败：', error);
    }
}

// 处理点赞（事件监听器版本，保留兼容）
async function handleLike(event) {
    // 确保获取到正确的按钮元素
    const likeBtn = event.target.closest('.like-btn') || event.target;
    handleLikeClick(likeBtn);
}

// 全局点赞处理函数，供HTML onclick属性直接调用
async function handleLikeClick(likeBtn) {
    const postId = likeBtn.dataset.postId;
    const likeCount = document.getElementById('like-count');
    
    console.log('点赞按钮点击，postId:', postId);
    
    try {
        const response = await fetch(`/post/${postId}/like`);
        console.log('点赞API响应状态:', response.status);
        
        const result = await response.json();
        console.log('点赞API响应结果:', result);
        
        if (result.success) {
            // 更新点赞数
            likeCount.textContent = result.likes;
            // 禁用点赞按钮，防止重复点赞
            likeBtn.disabled = true;
            likeBtn.style.backgroundColor = '#95a5a6';
            likeBtn.style.cursor = 'not-allowed';
            alert('点赞成功！');
        } else {
            alert('点赞失败：' + result.error);
        }
    } catch (error) {
        console.error('点赞失败：', error);
        alert('点赞失败，请检查网络连接后重试');
    }
}

// 处理评论提交
async function handleCommentSubmit(event) {
    // 阻止表单默认提交行为
    event.preventDefault();
    
    const commentForm = event.target;
    const postId = commentForm.dataset.postId;
    const formData = new FormData(commentForm);
    const commentContent = document.getElementById('comment-content');
    const commentsList = document.getElementById('commentsList');
    
    try {
        // 发送POST请求到后端API
        const response = await fetch(`/post/${postId}/comment`, {
            method: 'POST',
            body: formData
        });
        
        // 解析响应数据
        const result = await response.json();
        
        if (result.success) {
            // 清空评论输入框
            commentContent.value = '';
            
            // 创建新评论元素
            const commentElement = document.createElement('div');
            commentElement.className = 'comment-item';
            commentElement.innerHTML = `
                <div class="comment-header">
                    <span class="comment-author">${result.comment.author}</span>
                    <span class="comment-date">${result.comment.created_at}</span>
                </div>
                <div class="comment-content">${result.comment.content}</div>
            `;
            
            // 添加到评论列表顶部
            commentsList.insertBefore(commentElement, commentsList.firstChild);
            
            // 更新评论计数
            const commentsSection = commentForm.closest('.comments-section');
            const commentCount = commentsSection.querySelector('h3');
            const currentCount = parseInt(commentCount.textContent.match(/\d+/)[0]);
            commentCount.textContent = `评论 (${currentCount + 1})`;
        } else {
            alert('发表评论失败：' + result.error);
        }
    } catch (error) {
        console.error('发表评论失败：', error);
        alert('发表评论失败，请检查网络连接后重试');
    }
}