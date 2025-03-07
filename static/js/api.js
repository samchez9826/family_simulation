/**
 * API交互模块 - 处理与后端的所有通信
 */
const API = {
    // 基础URL，生产环境可能需要调整
    baseUrl: '',

    /**
     * 显示加载动画
     */
    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
    },

    /**
     * 隐藏加载动画
     */
    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    },

    /**
     * 发送请求的基础方法
     * @param {string} url - 请求地址
     * @param {string} method - 请求方法 (GET, POST等)
     * @param {Object} data - 请求数据
     * @returns {Promise} - 返回Promise
     */
    async sendRequest(url, method = 'GET', data = null) {
        this.showLoading();

        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(this.baseUrl + url, options);

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            this.hideLoading();

            return result;
        } catch (error) {
            this.hideLoading();
            console.error('API request failed:', error);
            throw error;
        }
    },

    /**
     * 获取游戏状态
     * @returns {Promise} - 游戏状态数据
     */
    async getGameState() {
        return this.sendRequest('/api/game_state');
    },

    /**
     * 创建新游戏
     * @returns {Promise} - 操作结果
     */
    async newGame() {
        return this.sendRequest('/api/new_game', 'POST');
    },

    /**
     * 创建角色
     * @param {Object} characterData - 角色信息
     * @returns {Promise} - 操作结果及创建的角色信息
     */
    async createCharacter(characterData) {
        return this.sendRequest('/api/create_character', 'POST', characterData);
    },

    /**
     * 执行活动
     * @param {string} activityType - 活动类型
     * @param {Object} params - 活动参数
     * @returns {Promise} - 活动结果
     */
    async doActivity(activityType, params = {}) {
        return this.sendRequest('/api/activity', 'POST', {
            activity_type: activityType,
            params
        });
    },

    /**
     * 进入下一天
     * @returns {Promise} - 操作结果
     */
    async nextDay() {
        return this.sendRequest('/api/next_day', 'POST');
    },

    /**
     * 保存游戏
     * @param {string} filename - 存档名称
     * @returns {Promise} - 操作结果
     */
    async saveGame(filename = 'autosave') {
        return this.sendRequest('/api/save_game', 'POST', { filename });
    },

    /**
     * 加载游戏
     * @param {string} filename - 存档名称
     * @returns {Promise} - 操作结果
     */
    async loadGame(filename) {
        return this.sendRequest('/api/load_game', 'POST', { filename });
    },

    /**
     * 获取存档列表
     * @returns {Promise} - 存档列表
     */
    async getSaves() {
        return this.sendRequest('/api/get_saves');
    }
};