/**
 * 游戏主逻辑模块
 */
const Game = {
    // 游戏状态
    gameState: null,

    /**
     * 初始化游戏
     */
    async init() {
        // 初始化UI
        UI.init();

        // 检查是否有保存的游戏
        try {
            const response = await API.getGameState();
            if (response && !response.error) {
                this.gameState = response;
                UI.updateGameUI();
                UI.showScreen('game-screen');
            } else {
                // 显示开始界面
                UI.showScreen('start-screen');
            }
        } catch (error) {
            console.error('Error checking game state:', error);
            // 显示开始界面
            UI.showScreen('start-screen');
        }
    },

    /**
     * 开始新游戏
     */
    async startNewGame() {
        try {
            const response = await API.newGame();
            if (response.status === 'success') {
                UI.showScreen('create-character-screen');
            } else {
                UI.showDialog('错误', '无法创建新游戏：' + response.message, [{ text: '确定' }]);
            }
        } catch (error) {
            UI.showDialog('错误', '无法创建新游戏：' + error.message, [{ text: '确定' }]);
        }
    },

    /**
     * 更新游戏状态
     * @param {Object} newState - 新的游戏状态
     */
    updateGameState(newState) {
        this.gameState = newState;
        UI.updateGameUI();
    },

    /**
     * 保存游戏
     * @param {string} filename - 存档名称
     */
    async saveGame(filename = 'autosave') {
        try {
            const response = await API.saveGame(filename);

            if (response.status === 'success') {
                UI.showDialog('保存成功', response.message, [{ text: '确定' }]);
            } else {
                UI.showDialog('保存失败', response.message, [{ text: '确定' }]);
            }
        } catch (error) {
            UI.showDialog('保存失败', error.message, [{ text: '确定' }]);
        }
    }
};

// 页面加载完成后初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    Game.init();
});