module.exports = {
    chainWebpack: config => {
        config.module.rules.delete('eslint');
    },
    pages: {
        proxy_form: {
            entry: 'src/pages/proxy_form/main.js',
            template: 'public/loading_index.html',
            filename: 'proxy_form.html',
            title: 'Proxy Bid Form'
        },

        proxy_view: {
            entry: 'src/pages/proxy_view/main.js',
            template: 'public/loading_index.html',
            filename: 'proxy_view.html',
            title: 'Your Proxy Bids'
        },

        logs: {
            entry: 'src/pages/log/main.js',
            template: 'public/loading_index.html',
            filename: 'log.html',
            title: 'Overview'
        },

        log_list: {
            entry: 'src/pages/log_list/main.js',
            template: 'public/loading_index.html',
            filename: 'log_list.html',
            title: 'All Logs'
        }

        // test: {
        //     entry: 'src/pages/test/main.js',
        //     template: 'public/index.html',
        //     filename: 'proxy.html',
        //     title: 'test'
        // },
    }
}