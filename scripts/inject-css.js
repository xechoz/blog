// 在 <head> 结束前注入自定义 CSS，不修改主题源码
hexo.extend.injector.register('head_end', () => {
    return '<link rel="stylesheet" href="' + hexo.config.root + 'css/custom.css">';
}, 'default');
