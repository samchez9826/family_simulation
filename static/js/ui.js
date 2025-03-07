/**
 * UI交互模块 - 处理界面操作和显示
 */
const UI = {
    /**
     * 初始化UI
     */
    init() {
        // 初始化标签页切换
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                // 移除所有active类
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

                // 添加active类到当前标签页
                btn.classList.add('active');
                const tabId = btn.getAttribute('data-tab') + '-tab';
                document.getElementById(tabId).classList.add('active');
            });
        });

        // 初始化活动按钮
        this.initActivityButtons();

        // 初始化其他按钮
        this.initButtons();
    },

    /**
     * 初始化活动按钮
     */
    initActivityButtons() {
        document.querySelectorAll('.activity-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const activity = btn.getAttribute('data-activity');
                this.handleActivity(activity);
            });
        });
    },

    /**
     * 初始化其他按钮
     */
    initButtons() {
        // 新游戏按钮
        document.getElementById('new-game-btn').addEventListener('click', () => {
            this.showScreen('create-character-screen');
        });

        // 加载游戏按钮
        document.getElementById('load-game-btn').addEventListener('click', async () => {
            try {
                const result = await API.getSaves();
                this.renderSaveFiles(result.saves);
                this.showScreen('load-game-screen');
            } catch (error) {
                this.showDialog('错误', '无法获取存档列表：' + error.message, [{ text: '确定' }]);
            }
        });

        // 游戏介绍按钮
        document.getElementById('game-intro-btn').addEventListener('click', () => {
            this.showScreen('game-intro-screen');
        });

        // 返回按钮
        document.getElementById('back-from-load').addEventListener('click', () => {
            this.showScreen('start-screen');
        });

        document.getElementById('back-from-intro').addEventListener('click', () => {
            this.showScreen('start-screen');
        });

        // 创建角色表单
        document.getElementById('character-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createCharacter();
        });

        // 随机角色按钮
        document.getElementById('create-random-btn').addEventListener('click', () => {
            this.createRandomCharacter();
        });

        // 结束当天按钮
        document.getElementById('end-day-btn').addEventListener('click', async () => {
            try {
                const result = await API.nextDay();
                Game.updateGameState(result.game_state);
                this.showDialog('新的一天', '你休息了一晚，精力已恢复。', [{ text: '确定' }]);
            } catch (error) {
                this.showDialog('错误', '无法结束当天：' + error.message, [{ text: '确定' }]);
            }
        });
    },

    /**
     * 处理活动选择
     * @param {string} activity - 活动类型
     */
    async handleActivity(activity) {
        try {
            // 特殊活动处理
            if (activity === 'status') {
                this.showCharacterDetails();
                return;
            }

            if (activity === 'family') {
                this.showFamilyTree();
                return;
            }

            // 需要参数的活动处理
            if (['study', 'investment', 'start_business', 'manage_business', 'mental_health', 'plastic_surgery', 'charity'].includes(activity)) {
                this.showActivityOptions(activity);
                return;
            }

            // 直接执行的活动
            const result = await API.doActivity(activity);
            if (result.success) {
                this.handleActivityResult(activity, result);
                Game.updateGameState(result.game_state);
            } else {
                this.showDialog('无法进行活动', result.message, [{ text: '确定' }]);
            }
        } catch (error) {
            this.showDialog('错误', '执行活动失败：' + error.message, [{ text: '确定' }]);
        }
    },

    /**
     * 处理活动结果
     * @param {string} activity - 活动类型
     * @param {Object} result - 活动结果
     */
    handleActivityResult(activity, result) {
        let title = '活动结果';
        let message = '';

        switch (activity) {
            case 'rest':
                title = '休息';
                message = `你进行了休息，恢复了${result.energy_gain}点精力。`;
                break;

            case 'work':
                title = '工作';
                if (result.message === '工作表现出色') {
                    message = `你今天工作表现出色，获得了基本工资¥${result.income.toFixed(2)}和额外奖金¥${result.bonus.toFixed(2)}！`;
                } else if (result.message === '工作表现不佳') {
                    message = `你今天工作表现不佳，仅获得了基本工资¥${result.income.toFixed(2)}，并且压力增加了。`;
                } else {
                    message = `你完成了一天的工作，赚取了¥${result.income.toFixed(2)}。`;
                }
                break;

            case 'exercise':
                title = '锻炼';
                message = `你进行了锻炼，健康增加了${result.health_gain}点，心情也变好了。`;
                if (result.mental_health_improvement > 0) {
                    message += `\n锻炼对你的心理健康也有积极影响。`;
                }
                break;

            case 'socialize':
                title = '社交';
                message = result.event;
                if (result.met_partner) {
                    message += `\n\n你遇到了一个有好感的对象：${result.partner.name}。`;
                    // 可以加入伴侣详情
                }
                break;

            case 'job_hunting':
                title = '求职';
                if (result.message === '求职成功') {
                    message = `恭喜！你找到了一份新工作：${result.new_job}，月薪¥${result.salary}。`;
                } else if (result.message === '换工作成功') {
                    const salaryChange = result.new_salary - result.old_salary;
                    const changeText = salaryChange > 0 ?
                        `增加了¥${salaryChange}` :
                        `减少了¥${Math.abs(salaryChange)}`;

                    message = `你从${result.old_job}换到了${result.new_job}，薪资${changeText}，现在为¥${result.new_salary}。`;
                } else if (result.message === '求职失败') {
                    message = '很遗憾，你的求职尝试失败了。';
                }
                break;

            case 'date':
                title = '约会';
                message = result.event || '你进行了一次约会活动。';

                if (result.relationship === '恋爱中') {
                    message += `\n\n恭喜！你与${result.partner.name}开始了一段恋爱关系。`;
                }
                break;

            default:
                message = '活动已完成。';
        }

        this.showDialog(title, message, [{ text: '确定' }]);
    },

    /**
     * 显示活动选项对话框
     * @param {string} activity - 活动类型
     */
    showActivityOptions(activity) {
        let title = '选择选项';
        let content = '';
        let options = [];

        switch (activity) {
            case 'study':
                title = '学习内容';
                content = '请选择要学习的内容：';
                options = [
                    { text: '专业知识 (+智商)', value: { focus: '专业知识' } },
                    { text: '财商 (+财商)', value: { focus: '财商' } },
                    { text: '情商 (+情商)', value: { focus: '情商' } },
                    { text: '领导能力 (+领导力)', value: { focus: '领导' } },
                    { text: '商业视野 (+商业眼光)', value: { focus: '商业' } },
                    { text: '取消', value: 'cancel' }
                ];
                break;

            case 'investment':
                title = '投资选项';
                content = '请选择投资类型：';
                options = [
                    { text: '股票 (高风险高回报)', value: { type: '股票' } },
                    { text: '基金 (中风险中回报)', value: { type: '基金' } },
                    { text: '债券 (低风险低回报)', value: { type: '债券' } },
                    { text: '房产 (长期稳定收益)', value: { type: '房产' } },
                    { text: '其他 (风险不定)', value: { type: '其他' } },
                    { text: '取消', value: 'cancel' }
                ];
                break;

            case 'start_business':
                title = '创业';
                content = '请选择创业类型：';
                options = [
                    { text: '科技公司', value: { type: '科技' } },
                    { text: '餐饮企业', value: { type: '餐饮' } },
                    { text: '零售商店', value: { type: '零售' } },
                    { text: '教育培训', value: { type: '教育' } },
                    { text: '咨询公司', value: { type: '咨询' } },
                    { text: '取消', value: 'cancel' }
                ];
                break;

            case 'manage_business':
                title = '企业管理';
                content = '请选择管理重点：';
                options = [
                    { text: '市场推广 (提升声誉)', value: { focus: '市场推广' } },
                    { text: '人才招聘 (扩大规模)', value: { focus: '人才招聘' } },
                    { text: '产品研发 (提高利润)', value: { focus: '产品研发' } },
                    { text: '成本控制 (稳定经营)', value: { focus: '成本控制' } },
                    { text: '战略调整 (长期发展)', value: { focus: '战略调整' } },
                    { text: '融资扩张 (快速增长)', value: { focus: '融资扩张' } },
                    { text: '取消', value: 'cancel' }
                ];
                break;

            case 'mental_health':
                title = '心理健康';
                content = '请选择心理健康护理方式：';
                options = [
                    { text: '自我调节 (效果弱)', value: { type: '自我调节' } },
                    { text: '朋友倾诉 (效果中)', value: { type: '朋友倾诉' } },
                    { text: '专业心理咨询 (效果强，费用¥3000)', value: { type: '专业心理咨询' } },
                    { text: '取消', value: 'cancel' }
                ];
                break;

            case 'plastic_surgery':
                title = '整容手术';
                content = '请选择整容类型：';
                options = [
                    { text: '微整形 (费用¥20000, 风险低, 效果小)', value: { type: '微整形' } },
                    { text: '面部整形 (费用¥50000, 风险中, 效果中)', value: { type: '面部整形' } },
                    { text: '全面改造 (费用¥150000, 风险高, 效果大)', value: { type: '全面改造' } },
                    { text: '取消', value: 'cancel' }
                ];
                break;

            case 'charity':
                title = '慈善捐款';
                content = '请选择捐款项目：';
                options = [
                    { text: '教育基金会 (最低¥1000)', value: { type: '教育基金会' } },
                    { text: '医疗救助 (最低¥5000)', value: { type: '医疗救助' } },
                    { text: '扶贫项目 (最低¥10000)', value: { type: '扶贫项目' } },
                    { text: '环保组织 (最低¥3000)', value: { type: '环保组织' } },
                    { text: '取消', value: 'cancel' }
                ];
                break;
        }

        this.showOptionsDialog(title, content, options, async (choice) => {
            if (choice === 'cancel') return;

            // 需要额外输入金额的活动
            if (['investment', 'charity'].includes(activity)) {
                this.showInputDialog('输入金额', `请输入${activity === 'investment' ? '投资' : '捐款'}金额：`, '1000', async (amount) => {
                    const numAmount = parseInt(amount);
                    if (isNaN(numAmount) || numAmount <= 0) {
                        this.showDialog('错误', '请输入有效金额', [{ text: '确定' }]);
                        return;
                    }

                    choice.amount = numAmount;
                    await this.executeActivity(activity, choice);
                });
            }
            // 需要企业名称的活动
            else if (activity === 'start_business') {
                this.showInputDialog('企业名称', '请输入您的企业名称：', `${Game.gameState.player.name}的${choice.type}公司`, async (name) => {
                    choice.name = name;
                    await this.executeActivity(activity, choice);
                });
            }
            // 其他直接执行的活动
            else {
                await this.executeActivity(activity, choice);
            }
        });
    },

    /**
     * 执行指定活动
     * @param {string} activity - 活动类型
     * @param {Object} params - 活动参数
     */
    async executeActivity(activity, params) {
        try {
            const result = await API.doActivity(activity, params);
            if (result.success) {
                this.handleActivityResult(activity, result);
                Game.updateGameState(result.game_state);
            } else {
                this.showDialog('无法进行活动', result.message, [{ text: '确定' }]);
            }
        } catch (error) {
            this.showDialog('错误', '执行活动失败：' + error.message, [{ text: '确定' }]);
        }
    },

    /**
     * 显示角色详细信息
     */
    showCharacterDetails() {
        const player = Game.gameState.player;
        if (!player) return;

        let content = `<div class="character-details">
            <h4>${player.name} (${player.gender}, ${player.age}岁)</h4>
            <div class="details-section">
                <h5>基本属性</h5>
                <div class="detail-item">健康: ${player.health}</div>
                <div class="detail-item">精力: ${player.energy}</div>
                <div class="detail-item">外貌: ${player.appearance}</div>
                <div class="detail-item">魅力: ${player.charm}</div>
                <div class="detail-item">智商: ${player.intelligence}</div>
                <div class="detail-item">情商: ${player.emotional_intelligence}</div>
                <div class="detail-item">财商: ${player.financial_intelligence}</div>
                <div class="detail-item">幸运: ${player.luck}</div>
            </div>

            <div class="details-section">
                <h5>身体状况</h5>
                <div class="detail-item">身高: ${player.height}cm</div>
                <div class="detail-item">体重: ${player.weight}kg</div>
                <div class="detail-item">体型: ${player.weight_status}</div>
            </div>

            <div class="details-section">
                <h5>心理状态</h5>
                <div class="detail-item">快乐度: ${player.happiness}</div>
                <div class="detail-item">压力水平: ${player.stress_level}</div>
                <div class="detail-item">心理状态: ${player.mental_state}</div>
            </div>

            <div class="details-section">
                <h5>经济状况</h5>
                <div class="detail-item">工作: ${player.job}</div>
                <div class="detail-item">月薪: ¥${player.salary}</div>
                <div class="detail-item">资产: ¥${player.assets.toFixed(2)}</div>
                <div class="detail-item">负债: ¥${player.debt.toFixed(2)}</div>
            </div>`;

        // 添加企业信息(如果有)
        if (player.has_business) {
            content += `
            <div class="details-section">
                <h5>企业信息</h5>
                <div class="detail-item">企业名称: ${player.business.name}</div>
                <div class="detail-item">类型: ${player.business.type}</div>
                <div class="detail-item">规模: ${player.business.scale}</div>
                <div class="detail-item">月利润: ¥${player.business.profit}</div>
                <div class="detail-item">企业价值: ¥${player.business.value}</div>
                <div class="detail-item">员工数: ${player.business.employees}</div>
                <div class="detail-item">声誉: ${player.business.reputation}</div>
            </div>`;
        }

        // 添加投资信息(如果有)
        if (player.investments && Object.values(player.investments).some(v => v > 0)) {
            content += `
            <div class="details-section">
                <h5>投资组合</h5>`;

            for (const [type, amount] of Object.entries(player.investments)) {
                if (amount > 0) {
                    content += `<div class="detail-item">${type}: ¥${amount.toFixed(2)}</div>`;
                }
            }

            content += `</div>`;
        }

        // 添加人脉网络信息
        content += `
        <div class="details-section">
            <h5>人脉网络</h5>`;

        for (const [type, level] of Object.entries(player.network)) {
            content += `<div class="detail-item">${type}圈: ${level}</div>`;
        }

        content += `</div></div>`;

        this.showDialog('角色详细信息', content, [{ text: '关闭' }]);
    },

    /**
     * 显示家族树
     */
    showFamilyTree() {
        const player = Game.gameState.player;
        const familyMembers = Game.gameState.family_members || [];

        if (!player) return;

        let content = `<div class="family-tree">
            <h4>家族成员</h4>`;

        // 分类展示家族成员
        const categories = {
            '配偶': [],
            '子女': [],
            '父母': [],
            '兄弟姐妹': [],
            '其他': []
        };

        // 分类家族成员
        for (const member of familyMembers) {
            if (player.spouse && member.name === player.spouse.name) {
                categories['配偶'].push(member);
            } else if (member.parents && member.parents.includes(player.name)) {
                categories['子女'].push(member);
            } else if (player.parents && player.parents.includes(member.name)) {
                categories['父母'].push(member);
            } else if (
                (player.parents && member.parents) &&
                player.parents.some(p => member.parents.includes(p))
            ) {
                categories['兄弟姐妹'].push(member);
            } else {
                categories['其他'].push(member);
            }
        }

        // 显示各分类
        for (const [category, members] of Object.entries(categories)) {
            if (members.length > 0) {
                content += `<div class="family-category">
                    <h5>${category}</h5>
                    <ul>`;

                for (const member of members) {
                    content += `<li>${member.name} (${member.gender}, ${member.age}岁, ${member.job})</li>`;
                }

                content += `</ul></div>`;
            }
        }

        // 添加家族总体信息
        content += `
        <div class="family-summary">
            <h5>家族统计</h5>
            <div>家族成员: ${familyMembers.length + 1}人</div>
            <div>家族财富: ¥${Game.gameState.family_fortune.toFixed(2)}</div>
            <div>家族声望: ${Game.gameState.family_prestige.toFixed(1)}</div>
        </div>`;

        content += `</div>`;

        this.showDialog('家族成员', content, [{ text: '关闭' }]);
    },

    /**
     * 创建角色
     */
    async createCharacter() {
        const name = document.getElementById('character-name').value.trim();
        const gender = document.querySelector('input[name="gender"]:checked').value;
        const age = parseInt(document.getElementById('character-age').value);
        const education = document.getElementById('education-level').value;

        try {
            const result = await API.createCharacter({
                name,
                gender,
                age,
                education
            });

            if (result.status === 'success') {
                Game.gameState = result.game_state;
                this.updateGameUI();
                this.showScreen('game-screen');

                // 显示欢迎对话框
                this.showDialog(
                    '游戏开始',
                    `欢迎来到家族兴衰模拟游戏！\n\n你将扮演${result.character.name}，开始人生旅程。请选择活动，努力发展自己和家族。`,
                    [{ text: '开始游戏' }]
                );
            } else {
                this.showDialog('错误', '角色创建失败。', [{ text: '确定' }]);
            }
        } catch (error) {
            this.showDialog('错误', '角色创建失败：' + error.message, [{ text: '确定' }]);
        }
    },

    /**
     * 创建随机角色
     */
    createRandomCharacter() {
        const genders = ['男性', '女性'];
        const gender = genders[Math.floor(Math.random() * genders.length)];
        const age = Math.floor(Math.random() * 30) + 18; // 18-47岁

        const educations = ['高中', '大专', '本科', '硕士', '博士'];
        const education = educations[Math.floor(Math.random() * educations.length)];

        // 更新表单
        document.getElementById('character-name').value = '';
        document.querySelectorAll('input[name="gender"]').forEach(input => {
            input.checked = input.value === gender;
        });
        document.getElementById('character-age').value = age;
        document.getElementById('education-level').value = education;
    },

    /**
     * 渲染存档文件列表
     * @param {Array} saveFiles - 存档文件列表
     */
    renderSaveFiles(saveFiles) {
        const savesList = document.getElementById('save-files-list');
        savesList.innerHTML = '';

        if (saveFiles.length === 0) {
            savesList.innerHTML = '<div class="no-saves">没有找到任何存档</div>';
            return;
        }

        for (const save of saveFiles) {
            const saveItem = document.createElement('div');
            saveItem.className = 'save-item';
            saveItem.innerHTML = `
                <div class="save-item-name">${save}</div>
            `;

            saveItem.addEventListener('click', () => this.loadSaveFile(save));
            savesList.appendChild(saveItem);
        }
    },

    /**
     * 加载存档文件
     * @param {string} filename - 存档文件名
     */
    async loadSaveFile(filename) {
        try {
            const result = await API.loadGame(filename);

            if (result.status === 'success') {
                Game.gameState = result.game_state;
                this.updateGameUI();
                this.showScreen('game-screen');

                this.showDialog('存档加载成功', `已加载存档：${filename}`, [{ text: '确定' }]);
            } else {
                this.showDialog('错误', '存档加载失败：' + result.message, [{ text: '确定' }]);
            }
        } catch (error) {
            this.showDialog('错误', '存档加载失败：' + error.message, [{ text: '确定' }]);
        }
    },

    /**
     * 显示指定屏幕
     * @param {string} screenId - 屏幕ID
     */
    showScreen(screenId) {
        // 隐藏所有屏幕
        document.querySelectorAll('section').forEach(section => {
            section.classList.add('hidden');
        });

        // 显示指定屏幕
        document.getElementById(screenId).classList.remove('hidden');

        // 特殊处理
        if (screenId === 'game-screen') {
            document.getElementById('game-info').classList.remove('hidden');
        } else {
            document.getElementById('game-info').classList.add('hidden');
        }
    },

    /**
     * 显示对话框
     * @param {string} title - 对话框标题
     * @param {string} message - 对话框内容
     * @param {Array} buttons - 按钮配置
     */
    showDialog(title, message, buttons) {
        const dialog = document.getElementById('dialog');
        const dialogTitle = document.getElementById('dialog-title');
        const dialogBody = document.getElementById('dialog-body');
        const dialogButtons = document.getElementById('dialog-buttons');

        // 设置内容
        dialogTitle.textContent = title;
        dialogBody.innerHTML = message;

        // 清除按钮
        dialogButtons.innerHTML = '';

        // 添加按钮
        for (const button of buttons) {
            const btn = document.createElement('button');
            btn.className = 'btn';
            if (button.primary) btn.classList.add('btn-primary');
            btn.textContent = button.text;

            btn.addEventListener('click', () => {
                dialog.classList.add('hidden');
                if (button.callback) button.callback();
            });

            dialogButtons.appendChild(btn);
        }

        // 显示对话框
        dialog.classList.remove('hidden');
    },

    /**
     * 显示选项对话框
     * @param {string} title - 对话框标题
     * @param {string} message - 对话框内容
     * @param {Array} options - 选项配置
     * @param {Function} callback - 回调函数
     */
    showOptionsDialog(title, message, options, callback) {
        const dialogButtons = options.map(option => ({
            text: option.text,
            primary: option.primary,
            callback: () => callback(option.value)
        }));

        this.showDialog(title, message, dialogButtons);
    },

    /**
     * 显示输入对话框
     * @param {string} title - 对话框标题
     * @param {string} message - 对话框内容
     * @param {string} defaultValue - 默认值
     * @param {Function} callback - 回调函数
     */
    showInputDialog(title, message, defaultValue, callback) {
        const inputId = 'dialog-input-' + Date.now();

        const content = `
            <p>${message}</p>
            <div class="dialog-form">
                <div class="form-group">
                    <input type="text" id="${inputId}" value="${defaultValue || ''}" />
                </div>
            </div>
        `;

        const buttons = [
            {
                text: '确定',
                primary: true,
                callback: () => {
                    const value = document.getElementById(inputId).value;
                    callback(value);
                }
            },
            {
                text: '取消',
                callback: () => {}
            }
        ];

        this.showDialog(title, content, buttons);

        // 聚焦输入框
        setTimeout(() => {
            const input = document.getElementById(inputId);
            if (input) input.focus();
        }, 100);
    },

    /**
     * 更新游戏界面
     */
    updateGameUI() {
        if (!Game.gameState || !Game.gameState.player) return;

        const player = Game.gameState.player;

        // 更新游戏信息
        document.getElementById('current-day').textContent = Game.gameState.current_day;
        document.getElementById('current-season').textContent = Game.gameState.current_season;
        document.getElementById('economy-status').textContent = `经济${Game.gameState.economy_status}`;
        document.getElementById('family-fortune').textContent = formatMoney(Game.gameState.family_fortune);
        document.getElementById('family-prestige').textContent = Game.gameState.family_prestige.toFixed(1);

        // 更新角色基本信息
        document.getElementById('character-name-display').textContent = player.name;
        document.getElementById('character-basic-info').textContent = `${player.gender} | ${player.age}岁`;

        // 更新属性条
        this.updateAttributeBar('health', player.health);
        this.updateAttributeBar('energy', player.energy);
        this.updateAttributeBar('appearance', player.appearance);
        this.updateAttributeBar('intelligence', player.intelligence);
        this.updateAttributeBar('emotional-intelligence', player.emotional_intelligence);
        this.updateAttributeBar('financial-intelligence', player.financial_intelligence);

        // 更新角色状态
        document.getElementById('job-value').textContent = player.job;
        document.getElementById('salary-value').textContent = `¥${player.salary}`;
        document.getElementById('assets-value').textContent = `¥${player.assets.toFixed(0)}`;
        document.getElementById('education-value').textContent = player.education_level;
        document.getElementById('relationship-value').textContent = player.relationship_status;

        // 更新事件列表
        this.updateEventsList();

        // 更新可用活动
        this.updateAvailableActivities();
    },

    /**
     * 更新属性条
     * @param {string} attributeName - 属性名
     * @param {number} value - 属性值
     */
    updateAttributeBar(attributeName, value) {
        const bar = document.getElementById(`${attributeName}-bar`);
        const valueDisplay = document.getElementById(`${attributeName}-value`);

        if (bar && valueDisplay) {
            const percentage = Math.min(100, Math.max(0, value));
            bar.style.width = `${percentage}%`;
            valueDisplay.textContent = Math.round(value);

            // 根据值设置颜色
            if (percentage < 25) {
                bar.style.backgroundColor = 'var(--danger-color)';
            } else if (percentage < 50) {
                bar.style.backgroundColor = 'var(--warning-color)';
            } else if (percentage < 75) {
                bar.style.backgroundColor = 'var(--primary-color)';
            } else {
                bar.style.backgroundColor = 'var(--success-color)';
            }
        }
    },

    /**
     * 更新事件列表
     */
    updateEventsList() {
        const eventsList = document.getElementById('events-list');
        eventsList.innerHTML = '';

        const events = Game.gameState.events || [];

        for (let i = events.length - 1; i >= 0; i--) {
            const event = events[i];
            const eventItem = document.createElement('div');
            eventItem.className = 'event-item';
            eventItem.innerHTML = `
                <div class="event-date">${event.date}</div>
                <div class="event-text">${event.event}</div>
            `;
            eventsList.appendChild(eventItem);
        }
    },

    /**
     * 更新可用活动
     */
    updateAvailableActivities() {
        // 实现根据角色状态动态调整可用活动
        // 这需要与后端配合，获取可用活动列表
        // 简化版本中，我们只针对一些典型条件进行处理

        const player = Game.gameState.player;

        // 工作活动
        const workBtn = document.querySelector('.activity-btn[data-activity="work"]');
        if (workBtn) {
            if (player.job === "无业") {
                workBtn.disabled = true;
                workBtn.classList.add('disabled');
            } else {
                workBtn.disabled = false;
                workBtn.classList.remove('disabled');
            }
        }

        // 创业活动
        const startBusinessBtn = document.querySelector('.activity-btn[data-activity="start_business"]');
        if (startBusinessBtn) {
            if (player.has_business || player.assets < 50000) {
                startBusinessBtn.disabled = true;
                startBusinessBtn.classList.add('disabled');
            } else {
                startBusinessBtn.disabled = false;
                startBusinessBtn.classList.remove('disabled');
            }
        }

        // 管理企业
        const manageBusinessBtn = document.querySelector('.activity-btn[data-activity="manage_business"]');
        if (manageBusinessBtn) {
            if (!player.has_business) {
                manageBusinessBtn.disabled = true;
                manageBusinessBtn.classList.add('disabled');
            } else {
                manageBusinessBtn.disabled = false;
                manageBusinessBtn.classList.remove('disabled');
            }
        }

        // 投资活动
        const investmentBtn = document.querySelector('.activity-btn[data-activity="investment"]');
        if (investmentBtn) {
            if (player.assets < 1000) {
                investmentBtn.disabled = true;
                investmentBtn.classList.add('disabled');
            } else {
                investmentBtn.disabled = false;
                investmentBtn.classList.remove('disabled');
            }
        }

        // 整容活动
        const plasticSurgeryBtn = document.querySelector('.activity-btn[data-activity="plastic_surgery"]');
        if (plasticSurgeryBtn) {
            if (player.assets < 20000) {
                plasticSurgeryBtn.disabled = true;
                plasticSurgeryBtn.classList.add('disabled');
            } else {
                plasticSurgeryBtn.disabled = false;
                plasticSurgeryBtn.classList.remove('disabled');
            }
        }
    }
};

/**
 * 格式化金额
 * @param {number} amount - 金额
 * @returns {string} - 格式化后的金额
 */
function formatMoney(amount) {
    if (amount >= 100000000) {  // 亿
        return `${(amount / 100000000).toFixed(2)}亿`;
    } else if (amount >= 10000) {  // 万
        return `${(amount / 10000).toFixed(1)}万`;
    } else {
        return `${amount.toFixed(0)}`;
    }
}