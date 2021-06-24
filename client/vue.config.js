module.exports = {
    chainWebpack: config => {
        config.module.rules.delete('eslint');
    },

    pages: {
        index: {
            entry: 'src/pages/home/main.js',
            template: 'public/index.html',
            filename: 'index.html',
            title: 'Proxy Bids'
        },
        timer: {
            entry: 'src/pages/timer/main.js',
            template: 'public/index.html',
            filename: 'timer.html',
            title: 'Auction Timer'
        }
    }
}