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

        // test: {
        //     entry: 'src/pages/test/main.js',
        //     template: 'public/index.html',
        //     filename: 'proxy.html',
        //     title: 'test'
        // },
    }
}