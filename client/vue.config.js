module.exports = {
    chainWebpack: config => {
        config.module.rules.delete('eslint');
    },
    pages: {
        proxy: {
            entry: 'src/pages/proxy_form/main.js',
            template: 'public/loading_index.html',
            filename: 'proxy_form.html',
            title: 'Proxy Bids'
        },

        // test: {
        //     entry: 'src/pages/test/main.js',
        //     template: 'public/index.html',
        //     filename: 'proxy.html',
        //     title: 'test'
        // },
    }
}